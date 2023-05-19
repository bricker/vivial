from datetime import datetime, timedelta
import eave.pubsub_schemas
import eave.stdlib
import eave.stdlib.core_api
import oauthlib.common
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

import eave.core.internal
import eave.core.internal.oauth.slack
import eave.core.internal.orm
from eave.core.internal.oauth import state_cookies as oauth_cookies
from eave.stdlib.logging import eaveLogger

from ...http_endpoint import HTTPEndpoint
from . import base, shared

_AUTH_PROVIDER = eave.stdlib.core_api.enums.AuthProvider.slack


class SlackOAuthAuthorize(HTTPEndpoint):
    async def get(self, request: Request) -> Response:
        # random value for verifying request wasnt tampered with via CSRF
        state: str = oauthlib.common.generate_token()
        authorization_url = eave.core.internal.oauth.slack.authorize_url_generator.generate(state)
        response = RedirectResponse(url=authorization_url)
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

        self.slack_oauth_data = slack_oauth_data = await eave.core.internal.oauth.slack.get_access_token_or_exception(
            code=self.code
        )
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

        await self._update_or_create_slack_installation()

        return self.response

    async def _update_or_create_slack_installation(
        self,
    ) -> None:
        slack_team_id = self.slack_oauth_data["team"]["id"]
        slack_bot_access_token = self.slack_oauth_data["access_token"]
        slack_bot_refresh_token = self.slack_oauth_data["refresh_token"]
        slack_token_expires_in = self.slack_oauth_data["expires_in"]
        log_context = self.eave_state.log_context_extras({"slack_team_id": slack_team_id})

        if not slack_token_expires_in:
            eaveLogger.warning(
                "Slack token didn't contain an expires_in value.",
                extra=log_context,
            )

        async with eave.core.internal.database.async_session.begin() as db_session:
            # try fetch existing slack installation
            slack_installation = await eave.core.internal.orm.SlackInstallationOrm.one_or_none(
                session=db_session,
                slack_team_id=slack_team_id,
            )

            if slack_installation and slack_installation.team_id != self.eave_account.team_id:
                eaveLogger.warning(
                    f"A Slack integration already exists with slack team id {slack_team_id}",
                    extra=log_context,
                )

                # TODO: Probably don't want to change the account's team like this, it feels like it could cause problems.
                # The reason we're doing this is because otherwise, connecting a Slack team silently fails if the Slack
                # team was already connected. Eventually we could perhaps display an error to the customer, but we don't
                # current have that.
                db_session.add(self.eave_account)
                self.eave_account.team_id = slack_installation.team_id
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
                    team_id=self.eave_account.team_id,
                    slack_team_id=slack_team_id,
                    bot_token=slack_bot_access_token,
                    bot_refresh_token=slack_bot_refresh_token,
                    bot_token_exp=(datetime.utcnow() + timedelta(seconds=slack_token_expires_in))
                    if slack_token_expires_in
                    else None,
                )

                await self._run_post_install_procedures(log_context=log_context)

    async def _run_post_install_procedures(
        self,
        log_context: eave.stdlib.typing.LogContext,
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

        except Exception:
            eaveLogger.exception("Error fetching Slack workspace user count", extra=log_context)

        eave.stdlib.analytics.log_event(
            event_name="eave_application_integration",
            event_description="An integration was added for a team",
            eave_account_id=self.eave_account.id,
            eave_team_id=self.eave_account.team_id,
            eave_visitor_id=self.eave_account.visitor_id,
            event_source="core api oauth",
            opaque_params={
                "integration_name": eave.stdlib.core_api.enums.Integration.slack.value,
                "approximate_num_members": approximate_num_members,
            },
        )

        try:
            slack_user_id = self.slack_oauth_data["authed_user"]["id"]
            await slack_client.chat_postMessage(
                channel=slack_user_id,
                text="Hey there! I’m Eave, and here to help with any of your documentation needs. Add me to channels or DMs, and simply tag me in a thread you want documented.",
            )
        except Exception:
            eaveLogger.exception("Error sending welcome message on Slack", extra=log_context)
