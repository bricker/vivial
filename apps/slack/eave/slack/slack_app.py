from typing import Optional

import eave.slack.event_handlers
from eave.slack.util import log_context
import eave.stdlib.core_api.client as eave_core
import eave.stdlib.core_api.operations as eave_ops
import eave.stdlib.exceptions
from eave.stdlib import logger
from slack_bolt.async_app import AsyncApp, AsyncBoltContext
from slack_bolt.authorization import AuthorizeResult
from slack_sdk.web.async_client import AsyncWebClient

from .config import app_config


class MissingSlackTeamIdError(Exception):
    pass

class MissingSlackClientError(Exception):
    pass

async def authorize(
    team_id: Optional[str], client: Optional[AsyncWebClient], context: AsyncBoltContext
) -> AuthorizeResult:
    """
    https://slack.dev/bolt-python/concepts#authorization
    https://github.com/slackapi/bolt-python/blob/f8c1b86a81690eb5b12cca40339102d23de1f7de/slack_bolt/middleware/authorization/async_multi_teams_authorization.py#L72-L77
    """
    extra = log_context(context)
    logger.debug("slack authorize request", extra=extra)

    # TODO: team_id can be None for org-wide installed apps
    # https://slack.dev/bolt-python/api-docs/slack_bolt/authorization/async_authorize.html
    if team_id is None:
        raise MissingSlackTeamIdError()

    if client is None:
        raise MissingSlackClientError()

    # Notes:
    # - context.bot_id, context.bot_token, and context.bot_user_id are all None in this function.
    # - context.team_id and context.user_id are available (barring org-wide installs mentioned above)

    # Raises for non-OK response.
    installation_data = await eave_core.get_slack_installation(
        input=eave_ops.GetSlackInstallation.RequestBody(
            slack_integration=eave_ops.SlackInstallationInput(
                slack_team_id=team_id,
            ),
        )
    )

    # TODO: We probably need the refresh token too.
    bot_token = installation_data.slack_integration.bot_token
    auth_test_response = await client.auth_test(token=bot_token)
    context["eave_team"] = installation_data.team

    # The following block of code is copied from
    # https://github.com/slackapi/bolt-python/blob/076efb5b0b6db849b074752cec0d406d3c747627/slack_bolt/authorization/authorize_result.py#L62-L93
    bot_user_id: Optional[str] = (
        auth_test_response.get("user_id") if auth_test_response.get("bot_id") is not None else None
    )
    user_id: Optional[str] = auth_test_response.get("user_id") if auth_test_response.get("bot_id") is None else None

    return AuthorizeResult(
        enterprise_id=auth_test_response.get("enterprise_id"),
        team_id=auth_test_response.get("team_id"),
        bot_id=auth_test_response.get("bot_id"),
        bot_user_id=bot_user_id,
        user_id=user_id,
        bot_token=bot_token,
        user_token=None,
    )


signing_secret = app_config.eave_slack_app_signing_secret

app = AsyncApp(
    signing_secret=signing_secret,
    url_verification_enabled=True,
    ssl_check_enabled=True,
    ignoring_self_events_enabled=True,
    request_verification_enabled=True,
    authorize=authorize,
)

eave.slack.event_handlers.register_event_handlers(app=app)
