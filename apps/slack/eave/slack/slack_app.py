from typing import Any
import eave.slack.event_handlers
import eave.stdlib.core_api.client as eave_client
import eave.stdlib.core_api.operations
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp
from slack_sdk.web.async_client import AsyncWebClient
from slack_bolt.authorization import AuthorizeResult

from .config import app_config


async def authorize(enterprise_id: str, team_id: str, logger: Any) -> AuthorizeResult:
    # TODO: team_id can be None for org-wide installed apps
    # https://slack.dev/bolt-python/api-docs/slack_bolt/authorization/async_authorize.html
    input = eave.stdlib.core_api.operations.GetSlackSource.RequestBody(
        slack_source=eave.stdlib.core_api.operations.SlackSourceInput(slack_team_id=team_id),
    )
    data = await eave_client.get_slack_source(input=input)
    assert data is not None
    assert data.slack_source is not None
    return AuthorizeResult(
        enterprise_id=enterprise_id,
        team_id=team_id,
        bot_token=data.slack_source.bot_token,
        bot_id=data.slack_source.bot_id,
        bot_user_id=data.slack_source.bot_user_id,
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
