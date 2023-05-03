import typing
import uuid
import eave.core.internal
import eave.core.internal.orm
import eave.core.internal.oauth.slack
import eave.core.internal.oauth.slack as eave_slack_oauth
import eave.stdlib
import eave.stdlib.core_api
import eave.core.public.requests.util
import fastapi
import oauthlib.common
from eave.core.internal.oauth import state_cookies as oauth_cookies
from . import shared

_AUTH_PROVIDER = eave.stdlib.core_api.enums.AuthProvider.slack

async def slack_oauth_authorize() -> fastapi.Response:
    # random value for verifying request wasnt tampered with via CSRF
    state: str = oauthlib.common.generate_token()
    authorization_url = eave.core.internal.oauth.slack.authorize_url_generator.generate(state)
    response = fastapi.responses.RedirectResponse(url=authorization_url)
    oauth_cookies.save_state_cookie(
        response=response,
        state=state,
        provider=_AUTH_PROVIDER,
    )
    return response


async def slack_oauth_callback(
    state: str,
    code: str,
    request: fastapi.Request,
    response: fastapi.Response,
) -> fastapi.Response:
    shared.verify_oauth_state_or_exception(state=state, auth_provider=_AUTH_PROVIDER, request=request, response=response)

    eave_state = eave.core.public.requests.util.get_eave_state(request=request)

    slack_oauth_data = await eave.core.internal.oauth.slack.get_access_token(code=code)
    slack_team_name = slack_oauth_data["team"]["name"]
    slack_team_id = slack_oauth_data["team"]["id"]
    slack_user_id = slack_oauth_data["authed_user"]["id"]
    slack_user_access_token = slack_oauth_data["authed_user"]["access_token"]
    slack_user_refresh_token = slack_oauth_data["authed_user"]["refresh_token"]
    slack_bot_access_token = slack_oauth_data["access_token"]
    slack_bot_refresh_token = slack_oauth_data["refresh_token"]

    user_identity = await eave.core.internal.oauth.slack.get_userinfo_or_exception(
        access_token=slack_user_access_token,
    )

    slack_user_name = user_identity.given_name
    slack_user_email = user_identity.email
    eave_team_name = slack_team_name or f"{slack_user_name}'s Team"

    eave_account = await shared.get_or_create_eave_account(
        request=request,
        response=response,
        eave_team_name=eave_team_name,
        user_email=slack_user_email,
        auth_provider=_AUTH_PROVIDER,
        auth_id=slack_user_id,
        access_token=slack_user_access_token,
        refresh_token=slack_user_refresh_token,
    )

    await _update_or_create_slack_installation(
        eave_state=eave_state,
        eave_account=eave_account,
        slack_team_id=slack_team_id,
        slack_bot_access_token=slack_bot_access_token,
        slack_bot_refresh_token=slack_bot_refresh_token,
    )

    return response


async def _update_or_create_slack_installation(
    eave_state: eave.core.public.requests.util.EaveRequestState,
    eave_account: eave.core.internal.orm.AccountOrm,
    slack_team_id: str,
    slack_bot_access_token: str,
    slack_bot_refresh_token: typing.Optional[str],
) -> None:
    async with eave.core.internal.database.async_session.begin() as db_session:
        # try fetch existing slack installation
        slack_installation = await eave.core.internal.orm.SlackInstallationOrm.one_or_none(
            session=db_session,
            slack_team_id=slack_team_id,
        )

        if slack_installation and slack_installation.team_id != eave_account.team_id:
            msg = f"A Slack integration already exists with slack team id {slack_team_id}"
            await eave_state.add_note(msg)
            eave.stdlib.logger.warning(msg, extra=eave_state.log_context)
            return

        if slack_installation:
            if slack_bot_access_token:
                slack_installation.bot_token = slack_bot_access_token
            if slack_bot_refresh_token:
                slack_installation.bot_refresh_token = slack_bot_refresh_token
        else:
            # create new slack installation associated with the TeamOrm
            slack_installation = await eave.core.internal.orm.SlackInstallationOrm.create(
                session=db_session,
                team_id=eave_account.team_id,
                slack_team_id=slack_team_id,
                bot_token=slack_bot_access_token,
                bot_refresh_token=slack_bot_refresh_token,
            )
