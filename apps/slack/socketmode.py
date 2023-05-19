import asyncio
import http
import time
from slack_bolt import BoltResponse
from slack_bolt.adapter.socket_mode.async_internals import send_async_response
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from slack_sdk.socket_mode.request import SocketModeRequest

import eave.stdlib.core_api.client
import eave.stdlib.lib.requests
import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.logging
from eave.stdlib.logging import eaveLogger
import eave.stdlib.time
from eave.slack.config import app_config
from eave.slack.slack_app import app as slack_app
from slack_sdk.socket_mode.aiohttp import SocketModeClient

eave.stdlib.time.set_utc()
eave.stdlib.lib.requests.set_origin(eave_origins.EaveOrigin.eave_slack_app)


class AsyncSocketModeWithImmediateAckHandler(AsyncSocketModeHandler):
    """
    This handler overrides the `handle` function to immediately `ack` the message from Slack, which allows
    the app to take its time processing the message.
    """

    async def handle(self, client: SocketModeClient, req: SocketModeRequest) -> None:  # type: ignore[override]
        start = time.time()
        eaveLogger.debug(req.payload)
        immediate_ack = BoltResponse(status=http.HTTPStatus.OK)
        await send_async_response(client, req, immediate_ack, start)
        await super().handle(client, req)


async def start_socket_mode() -> None:
    app_token = app_config.eave_slack_app_socketmode_token
    handler = AsyncSocketModeWithImmediateAckHandler(
        app=slack_app,
        app_token=app_token,
    )

    await handler.start_async()


if __name__ == "__main__":
    asyncio.run(start_socket_mode())
