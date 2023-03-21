import asyncio

from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from eave_slack.config import app_config
from eave_slack.slack_app import get_slack_app
from eave_slack.event_handlers import register_event_handlers

async def start_socket_mode() -> None:
    app = await get_slack_app()
    await register_event_handlers(app=app)

    app_token = await app_config.eave_slack_app_socketmode_token
    handler = AsyncSocketModeHandler(
        app=app,
        app_token=app_token,
    )

    await handler.start_async()

if __name__ == "__main__":
    asyncio.run(start_socket_mode())

