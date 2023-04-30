import typing

import eave.core.internal.database as eave_db
import eave.core.internal.oauth.slack as eave_slack_oauth
import eave.core.public.requests.util as request_util
import eave.stdlib.auth_cookies as eave_auth_cookies
import eave.stdlib.core_api.models as eave_models
import fastapi
import oauthlib.common
from eave.core.internal.config import app_config
from eave.core.internal.oauth import cookies as oauth_cookies
from eave.core.internal.orm.account import AccountOrm
from eave.core.internal.orm.auth_token import AuthTokenOrm
from eave.core.internal.orm.slack_installation import SlackInstallationOrm
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib.eave_origins import EaveOrigin
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.web.async_client import AsyncWebClient

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

    slack_oauth_data, slack_auth_test_data = await _finalize_slack_oauth(code=code)
    eave_account = await _login_eave_account(slack_oauth_data=slack_oauth_data, request=request, response=response)

    # OK, now the user is logged into their Eave account.
    # Next, we'll write down the information about the Slack Installation.

    async with eave_db.async_session.begin() as db_session:
        # try fetch slack installation for eave team
        slack_installation = await SlackInstallationOrm.one_or_none(
            session=db_session,
            team_id=eave_account.team_id,
        )

        if slack_installation is None:
            # create new slack installation associated with the TeamOrm
            slack_installation = await SlackInstallationOrm.create(
                session=db_session,
                team_id=eave_account.team_id,
                slack_team_id=slack_oauth_data.team.id,
                bot_token=slack_oauth_data.bot_token,
                bot_id=slack_auth_test_data.bot_id or "UNKNOWN",
                bot_user_id=slack_auth_test_data.bot_user_id,
            )
        else:
            slack_installation.slack_team_id = slack_oauth_data.team.id
            slack_installation.bot_token = slack_oauth_data.bot_token
            slack_installation.bot_id = slack_auth_test_data.bot_id or "UNKNOWN"
            slack_installation.bot_user_id = slack_auth_test_data.bot_user_id

    response = fastapi.responses.RedirectResponse(url=f"{app_config.eave_www_base}/dashboard")
    # clear state cookie now that it's been verified
    oauth_cookies.delete_state_cookie(response=response, provider=eave_models.AuthProvider.slack)
    return response


async def _login_eave_account(
    slack_oauth_data: eave_slack_oauth.SlackOAuthResponse, request: fastapi.Request, response: fastapi.Response
) -> AccountOrm:
    eave_state = request_util.get_eave_state(request=request)
    logged_in_account = await request_util.get_logged_in_account_if_present(request=request, response=response)
    if logged_in_account:
        return logged_in_account

    # User is not logged in.
    # So, they're logging in with Slack.
    # Check if an account already exists with this slack user ID and access token
    async with eave_db.async_session.begin() as db_session:
        eave_account = await AccountOrm.one_or_none(
            session=db_session,
            auth_provider=eave_models.AuthProvider.slack,
            auth_id=slack_oauth_data.authed_user.id,
        )

        if eave_account is not None:
            # An account exists. Update the saved auth tokens.
            eave_account.oauth_token = slack_oauth_data.authed_user.access_token
            eave_account.refresh_token = slack_oauth_data.authed_user.refresh_token
        else:
            # No account with that slack ID and slack oauth token was found.
            # Create a new account with a new team.
            # The Team is what is used for integrations, not an individual account.
            # TODO: If there is already a Team connected to the given Slack workspace, we could use that instead.
            eave_account = await _create_new_eave_account(slack_oauth_data=slack_oauth_data, eave_state=eave_state)

        auth_tokens = await AuthTokenOrm.create_token_pair_for_account(
            session=db_session,
            account=eave_account,
            audience=EaveOrigin.eave_www,
            log_context=eave_state.log_context,
        )

    # Set the cookie in the response headers.
    # This logs the user into their Eave account.
    eave_auth_cookies.set_auth_cookies(
        response=response, access_token=str(auth_tokens.access_token), refresh_token=str(auth_tokens.refresh_token)
    )

    return auth_tokens.account


async def _create_new_eave_account(
    slack_oauth_data: eave_slack_oauth.SlackOAuthResponse, eave_state: request_util.EaveRequestState
) -> AccountOrm:
    user_identity = await eave_slack_oauth.SlackIdentity.get(
        token=slack_oauth_data.authed_user.access_token, log_context=eave_state.log_context
    )

    # Default value
    beta_whitelisted = False

    if user_identity:
        if user_identity.email:
            beta_prewhitelist = app_config.eave_beta_prewhitelisted_emails
            beta_whitelisted = user_identity.email in beta_prewhitelist
        team_name = slack_oauth_data.team.name or f"{user_identity.given_name}'s Team"
    else:
        team_name = slack_oauth_data.team.name or "Your Team"

    async with eave_db.async_session.begin() as db_session:
        team = await TeamOrm.create(
            session=db_session,
            beta_whitelisted=beta_whitelisted,
            name=team_name,
            document_platform=None,
        )

        account_orm = await AccountOrm.create(
            session=db_session,
            team_id=team.id,
            auth_provider=eave_models.AuthProvider.slack,
            auth_id=slack_oauth_data.authed_user.id,
            oauth_token=slack_oauth_data.authed_user.access_token,
            refresh_token=slack_oauth_data.authed_user.refresh_token,
        )

    return account_orm


async def _finalize_slack_oauth(
    code: str,
) -> typing.Tuple[eave_slack_oauth.SlackOAuthResponse, eave_slack_oauth.SlackAuthTestResponse]:
    client = AsyncWebClient()

    # Complete the installation by calling oauth.v2.access API method
    access_token_response = await client.oauth_v2_access(
        client_id=app_config.eave_slack_client_id,
        client_secret=app_config.eave_slack_client_secret,
        code=code,
        redirect_uri=redirect_uri,
    )

    oauth_data = eave_slack_oauth.SlackOAuthResponse(response=access_token_response)
    bot_token = oauth_data.bot_token

    # oauth.v2.access doesn't include bot_id in response, so we have to fetch it
    auth_test_response = await client.auth_test(token=bot_token)
    auth_test_response.validate()
    auth_test_data = eave_slack_oauth.SlackAuthTestResponse(response=auth_test_response)
    return oauth_data, auth_test_data
