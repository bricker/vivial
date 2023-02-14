import asyncio
import json
import logging
from typing import Any, Optional

from pydantic import UUID4, EmailStr
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

import eave.public.requests as _requests
from eave.internal.json_object import JsonObject
from eave.internal.settings import APP_SETTINGS

slack_client = AsyncWebClient(token=APP_SETTINGS.eave_slack_system_bot_token)
slack_channels = {
    "sign_ups": "C04HH2N08LD",
}

_slacktasks = set[asyncio.Task[None]]()


def notify_slack(*args: Any, **kwargs: Any) -> None:
    task = asyncio.create_task(_task_notify_slack(*args, **kwargs))
    task.add_done_callback(_slacktasks.discard)
    _slacktasks.add(task)


async def _task_notify_slack(email: EmailStr, visitor_id: Optional[UUID4], opaque_input: Optional[JsonObject]) -> None:
    try:
        slackresponse = await slack_client.chat_postMessage(
            channel=slack_channels["sign_ups"],
            text=f"Someone signed up for early access!",
        )

        prettyjson = json.dumps(
            opaque_input,
            indent=2,
        )
        await slack_client.chat_postMessage(
            channel=slack_channels["sign_ups"],
            thread_ts=slackresponse.get("ts"),
            text=(f"Email: `{email}`\n" f"Visitor ID: `{visitor_id}`\n" f"```{prettyjson}```"),
        )
    except SlackApiError as e:
        logging.exception(e)
        raise e
