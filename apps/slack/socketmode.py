import asyncio
import logging

from eave.slack.config import app_config
from eave.slack.slack_app import app as slack_app
import eave.stdlib.logging
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

eave.stdlib.logging.setup_logging(level=logging.DEBUG)

async def start_socket_mode() -> None:
    app_token = app_config.eave_slack_app_socketmode_token
    handler = AsyncSocketModeHandler(
        app=slack_app,
        app_token=app_token,
    )

    await handler.start_async()


if __name__ == "__main__":
    asyncio.run(start_socket_mode())
