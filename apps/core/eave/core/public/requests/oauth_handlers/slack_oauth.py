import typing

import eave.core.internal
import eave.core.internal.oauth.slack
import eave.core.internal.orm
import eave.core.public.requests.util
import eave.pubsub_schemas
import eave.stdlib
import eave.stdlib.core_api
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
    request: fastapi.Request,
    response: fastapi.Response,
    state: str,
    code: typing.Optional[str] = None,
    error: typing.Optional[str] = None,
    error_description: typing.Optional[str] = None,
) -> fastapi.Response:
    shared.verify_oauth_state_or_exception(
        state=state, auth_provider=_AUTH_PROVIDER, request=request, response=response
    )

    eave_state = eave.core.public.requests.util.get_eave_state(request=request)

    if error or not code:
        eave.stdlib.logger.warning(
            f"Error response from Slack OAuth flow or code missing. {error}: {error_description}",
            extra=eave_state.log_context,
        )
        shared.set_redirect(response=response, location=eave.core.internal.app_config.eave_www_base)
        return response

    slack_oauth_data = await eave.core.internal.oauth.slack.get_access_token_or_exception(code=code)
    slack_team_name = slack_oauth_data["team"]["name"]
    slack_user_id = slack_oauth_data["authed_user"]["id"]
    slack_user_access_token = slack_oauth_data["authed_user"]["access_token"]
    slack_user_refresh_token = slack_oauth_data["authed_user"]["refresh_token"]

    slack_client = eave.core.internal.oauth.slack.get_authenticated_client(access_token=slack_user_access_token)
    user_identity = await eave.core.internal.oauth.slack.get_userinfo_or_exception(client=slack_client)

    slack_user_name = user_identity.given_name
    slack_user_email = user_identity.email

    if slack_team_name:
        eave_team_name = slack_team_name
    elif slack_user_name:
        eave_team_name = f"{slack_user_name}'s Team"
    else:
        eave_team_name = "Your Team"

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
        request=request, slack_oauth_data=slack_oauth_data, eave_account=eave_account
    )

    return response


async def _update_or_create_slack_installation(
    request: fastapi.Request,
    slack_oauth_data: eave.core.internal.oauth.slack.SlackOAuthResponse,
    eave_account: eave.core.internal.orm.AccountOrm,
) -> None:
    eave_state = eave.core.public.requests.util.get_eave_state(request=request)

    slack_team_id = slack_oauth_data["team"]["id"]
    slack_bot_access_token = slack_oauth_data["access_token"]
    slack_bot_refresh_token = slack_oauth_data["refresh_token"]

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

            await _run_post_install_procedures(
                request=request, slack_oauth_data=slack_oauth_data, eave_account=eave_account
            )


async def _run_post_install_procedures(
    request: fastapi.Request,
    slack_oauth_data: eave.core.internal.oauth.slack.SlackOAuthResponse,
    eave_account: eave.core.internal.orm.AccountOrm,
) -> None:
    eave_state = eave.core.public.requests.util.get_eave_state(request=request)

    slack_bot_access_token = slack_oauth_data["access_token"]
    slack_client = eave.core.internal.oauth.slack.get_authenticated_client(access_token=slack_bot_access_token)

    approximate_num_members = 0

    try:
        # Try to get the number of members in the Slack workspace.
        # This counts the number of people in the #general channel, but you can only find the #general channel by
        # looping through the entire list of channels.
        # Anyways, if there is any error for any reason, just abort and move on.
        cursor = None
        while True:
            channels_response = await slack_client.conversations_list(
                cursor=cursor,
                exclude_archived=True,
                types="public_channel",
            )
            assert isinstance(channels := channels_response.get("channels"), list), "Unexpected response data"
            candidates = list(filter(lambda c: c.get("name") == "general", channels))
            if len(candidates) > 0:
                approximate_num_members = candidates[0].get("num_members")
                break
            else:
                response_metadata = channels_response.get("response_metadata")
                if not response_metadata:
                    break
                assert isinstance(response_metadata, dict)
                cursor = response_metadata.get("next_cursor")
                if not cursor:
                    break

    except Exception as e:
        eave.stdlib.logger.error("Error fetching Slack workspace user count", exc_info=e, extra=eave_state.log_context)

    eave.stdlib.analytics.log_event(
        event_name="eave_application_integration",
        event_description="An integration was added for a team",
        eave_account_id=eave_account.id,
        eave_team_id=eave_account.team_id,
        eave_visitor_id=eave_account.visitor_id,
        event_source="core api oauth",
        opaque_params={
            "integration_name": eave.stdlib.core_api.enums.Integration.slack.value,
            "approximate_num_members": approximate_num_members,
        },
    )

    try:
        slack_user_id = slack_oauth_data["authed_user"]["id"]
        await slack_client.chat_postMessage(
            channel=slack_user_id,
            text="Hey there! I’m Eave, and here to help with any of your documentation needs. Add me to channels or DMs, and simply tag me in a thread you want documented.",
        )
    except Exception as e:
        eave.stdlib.logger.error("Error sending welcome message on Slack", exc_info=e, extra=eave_state.log_context)
