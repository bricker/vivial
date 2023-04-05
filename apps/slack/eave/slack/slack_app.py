from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp
from slack_sdk.web.async_client import AsyncWebClient

import eave.slack.event_handlers
from .config import app_config

token = app_config.eave_slack_bot_token
signing_secret = app_config.eave_slack_app_signing_secret

app = AsyncApp(
    token=token,
    signing_secret=signing_secret,
    url_verification_enabled=True,
    ssl_check_enabled=True,
    ignoring_self_events_enabled=True,
    request_verification_enabled=True,
)

eave.slack.event_handlers.register_event_handlers(app=app)

client = app.client

handler = AsyncSlackRequestHandler(app)
