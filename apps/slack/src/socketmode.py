import asyncio
import logging
import sys

from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

import eave.event_handlers
import eave.settings
import eave.slack

eave.event_handlers.ensure_import()


async def start_socket_mode() -> None:
    handler = AsyncSocketModeHandler(
        app=eave.slack.app,
        app_token=eave.settings.APP_SETTINGS.eave_slack_app_token,
    )

    await handler.start_async()


asyncio.run(start_socket_mode())
