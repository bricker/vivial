import logging
from typing import Optional

import eave.stdlib.util as eave_util
from slack_bolt.async_app import AsyncAck, AsyncApp

from . import brain, slack_models


async def register_event_handlers(app: AsyncApp) -> None:
    app.shortcut("eave_watch_request")(shortcut_eave_watch_request_handler)
    app.event("message")(event_message_handler)
    app.event("app_mention")(noop_handler)
    app.event("reaction_added")(noop_handler)
    app.event("file_deleted")(noop_handler)
    app.event("member_joined_channel")(noop_handler)


async def shortcut_eave_watch_request_handler(ack: AsyncAck, shortcut: Optional[eave_util.JsonObject]) -> None:
    logging.info("WatchRequestEventHandler %s", shortcut)
    await ack()
    assert shortcut is not None

    message_json = shortcut.get("message")
    assert message_json is not None

    # TODO: Use Shortcut slack model, and get shortcut actor
    channel = shortcut["channel"]["id"]
    message = slack_models.SlackMessage(message_json, channel=channel)
    b = brain.Brain(message=message)
    eave_util.do_in_background(b.process_shortcut_event())


async def event_message_handler(event: Optional[eave_util.JsonObject]) -> None:
    logging.info("MessageEventHandler %s", event)
    assert event is not None

    message = slack_models.SlackMessage(event)
    if message.subtype in ["bot_message", "bot_remove", "bot_add"]:
        # Ignore messages from bots.
        # TODO: We should accept messages from bots
        logging.info("ignoring bot message")
        return

    b = brain.Brain(message=message)
    eave_util.do_in_background(b.process_message())


async def noop_handler() -> None:
    pass
