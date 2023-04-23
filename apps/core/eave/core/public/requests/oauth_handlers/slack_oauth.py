from typing import Optional

import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import fastapi
import oauthlib.common
from eave.core.internal.config import app_config
from eave.core.internal.oauth import cookies as oauth_cookies
import eave.stdlib.core_api.models as eave_models
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.web.async_slack_response import AsyncSlackResponse

# Build https://slack.com/oauth/v2/authorize with sufficient query parameters
redirect_uri = f"{app_config.eave_api_base}/oauth/slack/callback"
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
    user_scopes=[
        "openid",
        "profile",
        "email",
    ],
    redirect_uri=redirect_uri,
)


class SlackTeam:
    id: str
    name: str

    def __init__(self, **kwargs: str):
        assert "id" in kwargs
        self.id = kwargs["id"]
        assert "name" in kwargs
        self.name = kwargs["name"]


class SlackAuthorizedUser:
    id: str
    access_token: str

    def __init__(self, **kwargs: str):
        assert "id" in kwargs
        self.id = kwargs["id"]
        assert "access_token" in kwargs
        self.access_token = kwargs["access_token"]


class SlackOAuthResponse:
    access_token: str
    team: SlackTeam
    authed_user: SlackAuthorizedUser

    def __init__(self, response: AsyncSlackResponse):
        access_token: Optional[str] = response.get("access_token")
        assert access_token is not None
        installed_team: dict[str, str] = response.get("team", {})
        installer: dict[str, str] = response.get("authed_user", {})

        self.access_token = access_token
        self.team = SlackTeam(**installed_team)
        self.authed_user = SlackAuthorizedUser(**installer)


async def slack_oauth_authorize() -> fastapi.Response:
    # random value for verifying request wasnt tampered with via CSRF
    state: str = oauthlib.common.generate_token()
    authorization_url = authorize_url_generator.generate(state)
    response = fastapi.responses.RedirectResponse(url=authorization_url)
    oauth_cookies.save_state_cookie(
        response=response,
        state=state,
        provider=eave_models.AuthProvider.slack,
    )
    return response


async def slack_oauth_callback(
    state: str, code: str, request: fastapi.Request, response: fastapi.Response
) -> fastapi.Response:
    # verify request not tampered
    cookie_state = oauth_cookies.get_state_cookie(request=request, provider=eave_models.AuthProvider.slack)
    assert state == cookie_state

    client = AsyncWebClient()
    # Complete the installation by calling oauth.v2.access API method
    raw_response = await client.oauth_v2_access(
        client_id=app_config.eave_slack_client_id,
        client_secret=app_config.eave_slack_client_secret,
        code=code,
        redirect_uri=redirect_uri,
    )

    oauth_data = SlackOAuthResponse(response=raw_response)
    bot_token = oauth_data.access_token
    slack_user_id = oauth_data.authed_user.id
    oauth_token = oauth_data.authed_user.access_token
    slack_team_id = oauth_data.team.id

    # oauth.v2.access doesn't include bot_id in response, so we have to fetch it
    auth_test = await client.auth_test(token=bot_token)
    bot_id: Optional[str] = auth_test.get("bot_id")
    assert bot_id is not None
    bot_user_id: Optional[str] = auth_test.get("user_id")

    # save our shiny new oauth token in db
    async with eave_db.get_async_session() as db_session:
        # try fetch existing team account from db
        # TODO: check session token once exists
        # https://github.com/eave-fyi/eave-monorepo/pull/3#discussion_r1160880115
        account_orm = await eave_orm.AccountOrm.one_or_none(
            session=db_session,
            auth_info=eave_models.AuthInfo(
                provider=eave_models.AuthProvider.slack,
                id=slack_user_id,
            ),
        )

        if account_orm is None:
            # If this is a new account, then also create a new team.
            # The Team is what is used for integrations, not an individual account.
            team = eave_orm.TeamOrm(
                name=team_name if (team_name := oauth_data.team.name) else "Your Team",
                document_platform=None,
            )

            db_session.add(team)
            await db_session.commit()

            account_orm = eave_orm.AccountOrm(
                team_id=team.id,
                auth_provider=eave_models.AuthProvider.slack,
                auth_id=slack_user_id,
                oauth_token=oauth_token,
            )

            db_session.add(account_orm)
        else:
            account_orm.oauth_token = oauth_token

        # try fetch slack installation for eave team
        slack_installation = await eave_orm.SlackInstallationOrm.one_or_none(
            team_id=account_orm.team_id,
            session=db_session,
        )

        if slack_installation is None:
            # create new slack installation associated with the TeamOrm
            slack_installation = eave_orm.SlackInstallationOrm(
                team_id=account_orm.team_id,
                slack_team_id=slack_team_id,
                bot_token=bot_token,
                bot_id=bot_id,
                bot_user_id=bot_user_id,
            )
            db_session.add(slack_installation)
        else:
            slack_installation.slack_team_id = slack_team_id
            slack_installation.bot_token = bot_token
            slack_installation.bot_id = bot_id
            slack_installation.bot_user_id = bot_user_id

        await db_session.commit()

    response = fastapi.responses.RedirectResponse(url=f"{app_config.eave_www_base}/dashboard")
    # clear state cookie now that it's been verified
    oauth_cookies.delete_state_cookie(response=response, provider=eave_models.AuthProvider.slack)
    return response
