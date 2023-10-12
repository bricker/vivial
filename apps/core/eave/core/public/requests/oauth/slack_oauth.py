from datetime import datetime, timedelta
import eave.pubsub_schemas
from eave.stdlib import utm_cookies
import eave.stdlib.analytics
import oauthlib.common
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

import eave.core.internal
import eave.core.internal.oauth.slack
import eave.core.internal.orm
from eave.core.internal.oauth import state_cookies as oauth_cookies
from eave.stdlib.core_api.models.account import AuthProvider
from eave.stdlib.core_api.models.integrations import Integration
from eave.core.internal.config import app_config
from eave.stdlib.logging import LogContext, eaveLogger

from eave.stdlib.http_endpoint import HTTPEndpoint
from . import EaveOnboardingErrorCode, base, shared

_AUTH_PROVIDER = AuthProvider.slack


class SlackOAuthAuthorize(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        # random value for verifying request wasnt tampered with via CSRF
        state: str = oauthlib.common.generate_token()
        authorization_url = eave.core.internal.oauth.slack.authorize_url_generator.generate(state)
        response = RedirectResponse(url=authorization_url)

        utm_cookies.set_tracking_cookies(
            response=response, request_cookies=request.cookies, query_params=request.query_params
        )

        oauth_cookies.save_state_cookie(
            response=response,
            state=state,
            provider=_AUTH_PROVIDER,
        )
        return response


class SlackOAuthCallback(base.BaseOAuthCallback):
    auth_provider = _AUTH_PROVIDER

    async def get(self, request: Request) -> Response:
        await super().get(request=request)

        # The self.code check here is mostly for the typechecker, as the _check_invalid_callback function also checks the value
        if not self.code or not self._check_valid_callback():
            return self.response

        self.slack_oauth_data = slack_oauth_data = await eave.core.internal.oauth.slack.get_access_token_or_exception(
            code=self.code
        )
        slack_team_name = slack_oauth_data["team"]["name"]
        slack_team_id = self.slack_oauth_data["team"]["id"]
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

        self.eave_account = await shared.get_or_create_eave_account(
            request=self.request,
            response=self.response,
            eave_team_name=eave_team_name,
            user_email=slack_user_email,
            auth_provider=_AUTH_PROVIDER,
            auth_id=slack_user_id,
            access_token=slack_user_access_token,
            refresh_token=slack_user_refresh_token,
        )

        async with eave.core.internal.database.async_session.begin() as db_session:
            self.eave_team = await self.eave_account.get_team(session=db_session)

        await self._update_or_create_slack_installation()

        slack_redirect_location = (
            f"https://slack.com/app_redirect?app={app_config.eave_slack_app_id}&team={slack_team_id}"
        )
        shared.set_redirect(response=self.response, location=slack_redirect_location)

        return self.response

    async def _update_or_create_slack_installation(
        self,
    ) -> None:
        slack_team_id = self.slack_oauth_data["team"]["id"]
        slack_team_name = self.slack_oauth_data["team"]["name"]
        slack_bot_access_token = self.slack_oauth_data["access_token"]
        slack_bot_refresh_token = self.slack_oauth_data["refresh_token"]
        slack_token_expires_in = self.slack_oauth_data["expires_in"]
        log_context = self.eave_state.ctx.set({"slack_team_id": slack_team_id})

        if not slack_token_expires_in:
            eaveLogger.warning(
                "Slack token didn't contain an expires_in value.",
                log_context,
            )

        async with eave.core.internal.database.async_session.begin() as db_session:
            # try fetch existing slack installation
            self.slack_installation = await eave.core.internal.orm.SlackInstallationOrm.one_or_none(
                session=db_session,
                slack_team_id=slack_team_id,
            )

            if self.slack_installation and self.slack_installation.team_id != self.eave_account.team_id:
                eaveLogger.warning(
                    f"A Slack integration already exists with slack team id {slack_team_id}",
                    log_context,
                )
                await eave.stdlib.analytics.log_event(
                    event_name="duplicate_integration_attempt",
                    event_source="core api slack oauth",
                    eave_account=self.eave_account.analytics_model,
                    eave_team=self.eave_team.analytics_model,
                    opaque_params={"integration": Integration.slack},
                    ctx=log_context,
                )

                shared.set_error_code(response=self.response, error_code=EaveOnboardingErrorCode.already_linked)
                return

            if self.slack_installation:
                if slack_bot_access_token:
                    self.slack_installation.bot_token = slack_bot_access_token
                if slack_bot_refresh_token:
                    self.slack_installation.bot_refresh_token = slack_bot_refresh_token
                if slack_team_name:
                    self.slack_installation.slack_team_name = slack_team_name
            else:
                # create new slack installation associated with the TeamOrm
                self.slack_installation = await eave.core.internal.orm.SlackInstallationOrm.create(
                    session=db_session,
                    team_id=self.eave_account.team_id,
                    slack_team_id=slack_team_id,
                    slack_team_name=slack_team_name,
                    bot_token=slack_bot_access_token,
                    bot_refresh_token=slack_bot_refresh_token,
                    bot_token_exp=(datetime.utcnow() + timedelta(seconds=slack_token_expires_in))
                    if slack_token_expires_in
                    else None,
                )

                await self._run_post_install_procedures(log_context=log_context)

    async def _run_post_install_procedures(
        self,
        log_context: LogContext,
    ) -> None:
        slack_bot_access_token = self.slack_oauth_data["access_token"]
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

                if not isinstance(channels := channels_response.get("channels"), list):
                    raise TypeError("slack channels: list expected")

                candidates = list(filter(lambda c: c.get("name") == "general", channels))
                if len(candidates) > 0:
                    approximate_num_members = candidates[0].get("num_members")
                    break
                else:
                    response_metadata = channels_response.get("response_metadata")
                    if not response_metadata:
                        break

                    if not isinstance(response_metadata, dict):
                        raise TypeError("slack response_metadata: dict expected")

                    cursor = response_metadata.get("next_cursor")
                    if not cursor:
                        break

        except Exception as e:
            eaveLogger.exception(e, log_context)

        await eave.stdlib.analytics.log_event(
            event_name="eave_application_integration",
            event_description="An integration was added for a team",
            event_source="core api slack oauth",
            eave_account=self.eave_account.analytics_model,
            eave_team=self.eave_team.analytics_model,
            opaque_params={
                "integration_name": Integration.slack.value,
                "approximate_num_members": approximate_num_members,
                "slack_team_name": self.slack_installation.slack_team_name if self.slack_installation else None,
            },
            ctx=log_context,
        )

        try:
            slack_user_id = self.slack_oauth_data["authed_user"]["id"]
            slack_bot_id = self.slack_oauth_data.get("bot_user_id")
            ref = f"<@{slack_bot_id}>" if slack_bot_id else "@Eave"

            message = (
                "Hey there, I’m Eave! I’m here to help with any of your documentation needs. Try the following:\n"
                f"  • Add me to any channels or DMs, and tag {ref} in a thread that you want documented\n"
                f"  • Tag {ref} in a message that includes GitHub links to document code\n"
                f"  • Tag {ref} to help look for existing documentation"
            )
            await slack_client.chat_postMessage(
                channel=slack_user_id,
                text=message,
            )
        except Exception as e:
            eaveLogger.exception(e, log_context)
