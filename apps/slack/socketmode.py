import asyncio

from eave.slack.config import app_config
from eave.slack.event_handlers import register_event_handlers
from eave.slack.slack_app import app as slack_app
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler


async def start_socket_mode() -> None:
    await register_event_handlers(app=slack_app)

    app_token = app_config.eave_slack_app_socketmode_token
    handler = AsyncSocketModeHandler(
        app=slack_app,
        app_token=app_token,
    )

    await handler.start_async()


if __name__ == "__main__":
    asyncio.run(start_socket_mode())
