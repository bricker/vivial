import typing

import eave.core.internal.database as eave_db
import eave.core.internal.oauth.slack as eave_slack_oauth
import eave.core.public.requests.util as request_util
import eave.stdlib.auth_cookies as eave_auth_cookies
import eave.stdlib.core_api.models
import eave.stdlib.core_api.enums
import fastapi
import oauthlib.common
from eave.core.internal.config import app_config
from eave.core.internal.oauth import state_cookies as oauth_cookies
from eave.core.internal.orm.account import AccountOrm
from eave.core.internal.orm.auth_token import AuthTokenOrm
from eave.core.internal.orm.slack_installation import SlackInstallationOrm
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib.eave_origins import EaveOrigin
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.web.async_client import AsyncWebClient
from eave.stdlib import logger
import eave.core.internal.oauth.slack
import eave.stdlib.exceptions
import sqlalchemy.exc

async def slack_oauth_authorize() -> fastapi.Response:
    # random value for verifying request wasnt tampered with via CSRF
    state: str = oauthlib.common.generate_token()
    authorization_url = eave.core.internal.oauth.slack.authorize_url_generator.generate(state)
    response = fastapi.responses.RedirectResponse(url=authorization_url)
    oauth_cookies.save_state_cookie(
        response=response,
        state=state,
        provider=eave.stdlib.core_api.enums.AuthProvider.slack,
    )
    return response


async def slack_oauth_callback(
    state: str, code: str, request: fastapi.Request,
) -> fastapi.Response:
    response = fastapi.responses.RedirectResponse(url=f"{app_config.eave_www_base}/dashboard")

    # verify request not tampered
    cookie_state = oauth_cookies.get_state_cookie(request=request, provider=eave.stdlib.core_api.enums.AuthProvider.slack)
    oauth_cookies.delete_state_cookie(response=response, provider=eave.stdlib.core_api.enums.AuthProvider.slack)
    assert state == cookie_state

    slack_oauth_data, slack_auth_test_data = await eave.core.internal.oauth.slack.get_access_token(code=code)
    eave_account = await _get_or_create_eave_account(slack_oauth_data=slack_oauth_data)
    await _update_or_create_slack_installation(eave_account=eave_account, slack_oauth_data=slack_oauth_data, slack_auth_test_data=slack_auth_test_data)


    # Set the cookie in the response headers.
    # This logs the user into their Eave account.
    eave_auth_cookies.set_auth_cookies(
        response=response,
        account_id=eave_account.id,
        access_token=eave_account.oauth_token,
    )

    return response

async def _update_or_create_slack_installation(eave_account: AccountOrm, slack_oauth_data: eave_slack_oauth.SlackOAuthResponse, slack_auth_test_data: eave_slack_oauth.SlackAuthTestResponse) -> None:
    async with eave_db.async_session.begin() as db_session:
        # try fetch existing slack installation
        slack_installation = await SlackInstallationOrm.one_or_none(
            session=db_session,
            slack_team_id=slack_oauth_data.team.id,
        )

        if slack_installation is None:
            # create new slack installation associated with the TeamOrm
            slack_installation = await SlackInstallationOrm.create(
                session=db_session,
                team_id=eave_account.team_id,
                slack_team_id=slack_oauth_data.team.id,
                bot_token=slack_oauth_data.bot_access_token,
                bot_refresh_token=slack_oauth_data.bot_refresh_token,
            )
        else:
            slack_installation.slack_team_id = slack_oauth_data.team.id
            slack_installation.bot_token = slack_oauth_data.bot_access_token
            slack_installation.bot_refresh_token = slack_oauth_data.bot_refresh_token

async def _get_or_create_eave_account(
    slack_oauth_data: eave_slack_oauth.SlackOAuthResponse
) -> AccountOrm:
    async with eave_db.async_session.begin() as db_session:
        eave_account = await AccountOrm.one_or_none(
            session=db_session,
            auth_provider=eave.stdlib.core_api.enums.AuthProvider.slack,
            auth_id=slack_oauth_data.authed_user.id,
        )

        if eave_account is not None:
            # An account exists. Update the saved auth tokens.
            eave_account.oauth_token = slack_oauth_data.authed_user.access_token
            eave_account.refresh_token = slack_oauth_data.authed_user.refresh_token

        else:
            # No account with that slack ID was found.
            # Create a new account with a new team.
            # The Team is what is used for integrations, not an individual account.
            # TODO: If there is already a Team connected to the given Slack workspace, we could use that instead.
            user_identity = await eave.core.internal.oauth.slack.get_userinfo_or_exception(
                token=slack_oauth_data.authed_user.access_token,
            )

            # Default value
            beta_whitelisted = False

            if user_identity.email:
                beta_prewhitelist = app_config.eave_beta_prewhitelisted_emails
                beta_whitelisted = user_identity.email in beta_prewhitelist

            team_name = slack_oauth_data.team.name or f"{user_identity.given_name}'s Team"

            eave_team = await TeamOrm.create(
                session=db_session,
                beta_whitelisted=beta_whitelisted,
                name=team_name,
                document_platform=None,
            )

            eave_account = await AccountOrm.create(
                session=db_session,
                team_id=eave_team.id,
                auth_provider=eave.stdlib.core_api.enums.AuthProvider.slack,
                auth_id=slack_oauth_data.authed_user.id,
                oauth_token=slack_oauth_data.authed_user.access_token,
                refresh_token=slack_oauth_data.authed_user.refresh_token,
            )

            # auth_tokens = await AuthTokenOrm.create_token_pair_for_account(
            #     session=db_session,
            #     account=eave_account,
            #     audience=EaveOrigin.eave_www,
            #     log_context=eave_state.log_context,
            # )

        return eave_account