from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp

from eave.settings import APP_SETTINGS

app = AsyncApp(
    token=APP_SETTINGS.eave_slack_bot_token,
    signing_secret=APP_SETTINGS.eave_slack_bot_signing_secret,
)

client = app.client
handler = AsyncSlackRequestHandler(app)


async def start_socket_mode() -> None:
    await AsyncSocketModeHandler(app, APP_SETTINGS.eave_slack_app_token).start_async()
