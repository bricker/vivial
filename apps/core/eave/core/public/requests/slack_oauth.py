from typing import Optional

import fastapi
import pydantic
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.installation_store import FileInstallationStore, Installation
from slack_sdk.oauth.state_store import FileOAuthStateStore
from slack_sdk.web import WebClient, SlackResponse

import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as eave_models
from eave.core.internal.config import app_config
from . import oauth_cookies as oauth


# factory for for tamper-detection code (convert to generator function?)
# TODO: where are the docs for this stupid thing??
# probs shouldnt write to random ./data dir
state_store = FileOAuthStateStore(expiration_seconds=300, base_dir="./data")

# Build https://slack.com/oauth/v2/authorize with sufficient query parameters
authorize_url_generator = AuthorizeUrlGenerator(
    client_id=app_config.eave_slack_client_id,
    scopes=[
        "app_mentions:read",
        "channels:history",
        "channels:read",
        "chat:write",
        "commands",
        "files:read",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "im:write",
        "links.embed:write",
        "links:read",
        "links:write",
        "metadata.message:read",
        "mpim:history",
        "mpim:read",
        "mpim:write",
        "pins:read",
        "reactions:read",
        "reactions:write",
        "team:read",
        "usergroups:read",
        "users.profile:read",
        "users:read",
        "users:read.email",
    ],
    user_scopes=[],
    redirect_uri=f"{app_config.eave_api_base}/oauth/slack/callback",
)


# TODO: any params input to callback. keep separate from google one?
class RequestBody(pydantic.BaseModel):
    state: Optional[str]
    code: Optional[str]
    error: Optional[str]


# GET
async def slack_oauth_authorize() -> fastapi.responses.RedirectResponse:
    # random value for verifying request wasnt tampered with
    state: str = state_store.issue()

    authorization_url = authorize_url_generator.generate(state)
    response = fastapi.responses.RedirectResponse(url=authorization_url)
    oauth.save_state_cookie(response=response, state=state)
    return response


# GET TODO: does slack expect a response from this? docs send back some generic string
async def slack_oauth_callback(input: RequestBody, request: fastapi.Request, response: fastapi.Response) -> None:
    # TODO: check input for error?
    state = oauth.get_state_cookie(request=request)
    assert state_store.consume(
        state=state
    )  # TODO: more graceful err handling? "Try the installation again (the state value is already expired)""

    client = WebClient()
    # Complete the installation by calling oauth.v2.access API method
    oauth_response: SlackResponse = client.oauth_v2_access(
        client_id=app_config.eave_slack_client_id,
        client_secret=app_config.eave_slack_client_secret,
        code=input.code,
    )

    is_enterprise_install: bool = oauth_response.get("is_enterprise_install", False)
    installed_team: dict[str, str] = oauth_response.get("team", {})
    installer: dict[str, str] = oauth_response.get("authed_user", {})
    user_id: Optional[str] = installer.get("id")
    assert user_id is not None

    bot_token: Optional[str] = oauth_response.get("access_token")
    # we are authing a slack bot, so this should never be None
    assert bot_token is not None

    # oauth.v2.access doesn't include bot_id in response
    # TODO: what is bot_id?
    bot_id = None
    enterprise_url = None
    auth_test = client.auth_test(token=bot_token)
    bot_id = auth_test["bot_id"]
    # TODO: do we need this?
    if is_enterprise_install:
        enterprise_url = auth_test.get("url")

    # save our shiny new oauth token in db
    async with await eave_db.get_session() as session:
        # try fetch existing team account from db
        account_orm = await eave_orm.AccountOrm.one_or_none(
            session=session,
            auth_provider=eave_orm.AuthProvider.slack,
            auth_id=user_id,
        )

        if account_orm is None:
            # If this is a new account, then also create a new team.
            # The Team is what is used for integrations, not an individual account.
            team_name = installed_team.get("name")
            team = eave_orm.TeamOrm(
                name=f"{team_name}'s Team" if team_name is not None else "Your Team",
                document_platform=eave_models.DocumentPlatform.unspecified,
            )

            session.add(team)
            await session.commit()

            account_orm = eave_orm.AccountOrm(
                team_id=team.id, auth_provider=eave_orm.AuthProvider.slack, auth_id=user_id, oauth_token=bot_token
            )

            session.add(account_orm)

        account_orm.oauth_token = bot_token
        await session.commit()

    response = fastapi.responses.RedirectResponse(url=f"{app_config.eave_www_base}/setup")
    oauth.delete_state_cookie(response=response)
    # TODO: return response?
