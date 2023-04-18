from typing import Any, Optional

import eave.slack.event_handlers
import eave.stdlib.core_api.client as eave_client
import eave.stdlib.core_api.operations as eave_ops
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp, AsyncBoltContext
from slack_bolt.authorization import AuthorizeResult
from slack_sdk.web.async_client import AsyncWebClient

from .config import app_config


async def authorize(
    enterprise_id: Optional[str], team_id: Optional[str], user_id: Optional[str], context: AsyncBoltContext
) -> AuthorizeResult:
    """
    https://slack.dev/bolt-python/concepts#authorization
    https://github.com/slackapi/bolt-python/blob/f8c1b86a81690eb5b12cca40339102d23de1f7de/slack_bolt/middleware/authorization/async_multi_teams_authorization.py#L72-L77
    """
    # TODO: team_id can be None for org-wide installed apps
    # https://slack.dev/bolt-python/api-docs/slack_bolt/authorization/async_authorize.html
    assert team_id is not None

    # Notes:
    # - context.bot_id, context.bot_token, and context.bot_user_id are all None in this function.
    # - context.team_id and context.user_id are available (barring org-wide installs mentioned above)

    input = eave_ops.GetSlackInstallation.RequestBody(
        slack_installation=eave_ops.SlackInstallationInput(slack_team_id=team_id),
    )
    data = await eave_client.get_slack_installation(input=input)
    assert data is not None

    # context inherits dict
    context["eave_team"] = data.team

    return AuthorizeResult(
        enterprise_id=enterprise_id,
        team_id=team_id,
        bot_token=data.slack_installation.bot_token,
        bot_id=data.slack_installation.bot_id,
        bot_user_id=data.slack_installation.bot_user_id,
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

client = app.client

handler = AsyncSlackRequestHandler(app)
