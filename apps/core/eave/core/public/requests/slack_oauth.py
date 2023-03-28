from typing import Optional

import fastapi
import pydantic
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.oauth.installation_store import FileInstallationStore, Installation
from slack_sdk.oauth.state_store import FileOAuthStateStore
from slack_sdk.web import WebClient

import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as eave_models
from eave.core.internal.config import app_config
from . import oauth_cookies as oauth


# factory for for tamper-detection code (convert to generator function?)
# TODO: link docs
state_store = FileOAuthStateStore(expiration_seconds=300, base_dir="./data")

# Persist installation data and lookup it by IDs.
installation_store = FileInstallationStore(base_dir="./data")  # TODO: what do these base dirs mean?

# Build https://slack.com/oauth/v2/authorize with sufficient query parameters
authorize_url_generator = AuthorizeUrlGenerator(
    client_id=app_config.eave_slack_client_id,
    # TODO: better way to keep these in sync w/ actual app settings?
    scopes=[
        "app_mentions:read",
        "bookmarks:read",
        "bookmarks:write",
        "calls:read",
        "calls:write",
        "channels:history",
        "channels:manage",
        "channels:read",
        "chat:write",
        "commands",
        "dnd:read",
        "files:read",
        "files:write",
        "groups:history",
        "groups:read",
        "groups:write",
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
        "pins:write",
        "reactions:read",
        "reactions:write",
        "team:read",
        "usergroups:read",
        "usergroups:write",
        "users.profile:read",
        "users:read",
        "users:read.email",
    ],
    user_scopes=[],
)


# TODO: any params input to callback. keep separate from google one?
class RequestBody(pydantic.BaseModel):
    state: Optional[str]
    code: Optional[str]
    error: Optional[str]


# GET
async def slack_oauth_authorize() -> fastapi.responses.RedirectResponse:
    # Generate a random value and store it on the server-side
    state: str = state_store.issue()

    authorization_url = authorize_url_generator.generate(state)
    response = fastapi.responses.RedirectResponse(url=authorization_url)
    oauth.save_state_cookie(response=response, state=state)
    return response


# GET TODO: does slack expect a response from this? docs send back some generic string
async def slack_oauth_callback(input: RequestBody, request: fastapi.Request, response: fastapi.Response) -> None:
    state = oauth.get_state_cookie(request=request)
    assert state_store.consume(
        state=state
    )  # TODO: more graceful handling? Try the installation again (the state value is already expired)

    redirect_uri = f"{app_config.eave_www_base}/setup"
    client = WebClient()
    # Complete the installation by calling oauth.v2.access API method
    oauth_response = client.oauth_v2_access(
        client_id=app_config.eave_slack_client_id,
        client_secret=app_config.eave_slack_client_secret,
        redirect_uri=redirect_uri,
        code=request.args["code"],
    )

    installed_enterprise = oauth_response.get("enterprise", {})
    is_enterprise_install = oauth_response.get("is_enterprise_install")
    installed_team = oauth_response.get("team", {})
    installer = oauth_response.get("authed_user", {})
    incoming_webhook = oauth_response.get("incoming_webhook", {})

    bot_token = oauth_response.get("access_token")
    # NOTE: oauth.v2.access doesn't include bot_id in response
    bot_id = None
    enterprise_url = None
    if bot_token is not None:
        auth_test = client.auth_test(token=bot_token)
        bot_id = auth_test["bot_id"]
        if is_enterprise_install is True:
            enterprise_url = auth_test.get("url")

    installation = Installation(
        app_id=oauth_response.get("app_id"),
        enterprise_id=installed_enterprise.get("id"),
        enterprise_name=installed_enterprise.get("name"),
        enterprise_url=enterprise_url,
        team_id=installed_team.get("id"),
        team_name=installed_team.get("name"),
        bot_token=bot_token,
        bot_id=bot_id,
        bot_user_id=oauth_response.get("bot_user_id"),
        bot_scopes=oauth_response.get("scope"),  # comma-separated string
        user_id=installer.get("id"),
        user_token=installer.get("access_token"),
        user_scopes=installer.get("scope"),  # comma-separated string
        incoming_webhook_url=incoming_webhook.get("url"),
        incoming_webhook_channel=incoming_webhook.get("channel"),
        incoming_webhook_channel_id=incoming_webhook.get("channel_id"),
        incoming_webhook_configuration_url=incoming_webhook.get("configuration_url"),
        is_enterprise_install=is_enterprise_install,
        token_type=oauth_response.get("token_type"),
    )

    # Store the installation
    installation_store.save(installation)

    # save our shiny new oauth token in db
    async with await eave_db.get_session() as session:
        account_orm = await eave_orm.AccountOrm.one_or_none(
            session=session,
            auth_provider=eave_orm.AuthProvider.google,
            auth_id=userid,
        )

        if account_orm is None:
            # If this is a new account, then also create a new team.
            # The Team is what is used for integrations, not an individual account.
            team = eave_orm.TeamOrm(
                name=f"{given_name}'s Team" if given_name is not None else "Your Team",
                document_platform=eave_models.DocumentPlatform.unspecified,
            )

            session.add(team)
            await session.commit()

            account_orm = eave_orm.AccountOrm(
                team_id=team.id,
                auth_provider=eave_orm.AuthProvider.google,
                auth_id=userid,
                oauth_token=credentials.id_token,
            )

            session.add(account_orm)

        account_orm.oauth_token = credentials.id_token
        await session.commit()

    response = fastapi.responses.RedirectResponse(url=redirect_uri)
    oauth.delete_state_cookie(response=response)
    # return response?
