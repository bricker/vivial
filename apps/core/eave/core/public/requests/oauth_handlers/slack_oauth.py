from typing import Optional
import fastapi
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.web import WebClient, SlackResponse

import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.models as eave_models
from eave.core.internal.config import app_config

from . import oauth_cookie as oauth
from . import oauth_state


# Build https://slack.com/oauth/v2/authorize with sufficient query parameters
# TODO: no ngrok
redirect_uri = "https://1848-2601-281-8100-82b0-00-928.ngrok.io/oauth/slack/callback"  # f"{app_config.eave_api_base}/oauth/slack/callback"
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
    redirect_uri=redirect_uri,
)


async def slack_oauth_authorize() -> fastapi.Response:
    # random value for verifying request wasnt tampered with
    state: str = oauth_state.generate_token()
    authorization_url = authorize_url_generator.generate(state)
    response = fastapi.responses.RedirectResponse(url=authorization_url)
    oauth.save_state_cookie(response=response, state=state)
    return response


async def slack_oauth_callback(
    state: str,
    code: str,
    request: fastapi.Request,
    response: fastapi.Response
) -> fastapi.Response:
    # verify request not tampered
    cookie_state = oauth.get_state_cookie(request=request)
    assert state == cookie_state

    client = WebClient()
    # Complete the installation by calling oauth.v2.access API method
    oauth_response: SlackResponse = client.oauth_v2_access(
        client_id=app_config.eave_slack_client_id,
        client_secret=app_config.eave_slack_client_secret,
        code=code,
        redirect_uri=redirect_uri,
    )

    installed_team: dict[str, str] = oauth_response.get("team", {})
    installer: dict[str, str] = oauth_response.get("authed_user", {})
    user_id: Optional[str] = installer.get("id")  # TODO: this probs isnt the user_id i want (this is slack user id)
    slack_team_id: Optional[str] = installed_team.get("id")
    assert user_id is not None
    assert slack_team_id is not None

    bot_token: Optional[str] = oauth_response.get("access_token")
    # we are authing a slack bot, so this should never be None
    assert bot_token is not None

    # save our shiny new oauth token in db
    async with await eave_db.get_session() as session:
        # try fetch existing team account from db
        account_orm = await eave_orm.AccountOrm.one_or_none(
            session=session,
            auth_provider=eave_orm.AuthProvider.slack,
            auth_id=user_id,  # TODO: pretty sure this param isnt right value
        )

        if account_orm is None:
            # If this is a new account, then also create a new team.
            # The Team is what is used for integrations, not an individual account.
            team_name = installed_team.get("name")
            team = eave_orm.TeamOrm(
                name=team_name if team_name is not None else "Your Team",
                document_platform=None,
            )

            session.add(team)
            await session.commit()

            account_orm = eave_orm.AccountOrm(
                team_id=team.id, auth_provider=eave_orm.AuthProvider.slack, auth_id=user_id, oauth_token=bot_token
            )

            session.add(account_orm)

        # assert account_orm is not None

        # try fetch slack source for eave team
        slack_source = await eave_orm.SlackSource.one_or_none(team_id=account_orm.team_id, session=session)

        if slack_source is None:
            # create new slack source associated with the TeamOrm
            slack_source = eave_orm.SlackSource(team_id=account_orm.team_id, slack_team_id=slack_team_id)
            session.add(slack_source)

        slack_source.slack_team_id = slack_team_id
        account_orm.oauth_token = bot_token
        await session.commit()

    response = fastapi.responses.RedirectResponse(url=f"{app_config.eave_www_base}/setup")
    oauth.delete_state_cookie(response=response)
    return response
