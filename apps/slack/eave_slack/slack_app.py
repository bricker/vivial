from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp
from slack_sdk.web.async_client import AsyncWebClient

from .config import app_config

_app: AsyncApp | None = None
async def get_slack_app() -> AsyncApp:
    global _app
    if _app is not None:
        return _app

    token = await app_config.eave_slack_bot_token
    signing_secret = await app_config.eave_slack_app_signing_secret

    _app = AsyncApp(
        token=token,
        signing_secret=signing_secret,
        url_verification_enabled=True,
        ssl_check_enabled=True,
        ignoring_self_events_enabled=True,
        request_verification_enabled=True,
    )

    return _app

async def get_slack_client() -> AsyncWebClient:
    app = await get_slack_app()
    return app.client

_handler: AsyncSlackRequestHandler | None = None
async def get_slack_app_handler() -> AsyncSlackRequestHandler:
    global _handler
    if _handler is not None:
        return _handler

    app = await get_slack_app()
    _handler = AsyncSlackRequestHandler(app)
    return _handler