import asyncio
import logging
from typing import Optional

from slack_bolt.async_app import AsyncAck, AsyncApp

import eave.brain
import eave.slack
import eave.slack_models
import eave.util


def ensure_import() -> None:
    pass


@eave.slack.app.shortcut("eave_watch_request")
async def shortcut_eave_watch_request_handler(ack: AsyncAck, shortcut: Optional[eave.util.JsonObject]) -> None:
    logging.info("WatchRequestEventHandler %s", shortcut)
    await ack()
    assert shortcut is not None

    message_json = shortcut.get("message")
    assert message_json is not None

    # TODO: Use Shortcut slack model, and get shortcut actor
    channel = shortcut["channel"]["id"]
    message = eave.slack_models.SlackMessage(message_json, channel=channel)
    brain = eave.brain.Brain(message=message)
    eave.util.do_in_background(brain.process_shortcut_event())


@eave.slack.app.event("message")
async def event_message_handler(event: Optional[eave.util.JsonObject]) -> None:
    logging.info("MessageEventHandler %s", event)
    assert event is not None

    message = eave.slack_models.SlackMessage(event)
    if message.subtype in ["bot_message", "bot_remove", "bot_add"]:
        # Ignore messages from bots.
        # TODO: We should accept messages from bots
        logging.info("ignoring bot message")
        return

    brain = eave.brain.Brain(message=message)
    eave.util.do_in_background(brain.process_message())


@eave.slack.app.event("url_verification")
async def event_url_verification_handler(event: eave.util.JsonObject) -> str:
    challenge = event["challenge"]
    assert isinstance(challenge, str)
    return challenge


@eave.slack.app.event("app_mention")
@eave.slack.app.event("reaction_added")
@eave.slack.app.event("file_deleted")
@eave.slack.app.event("member_joined_channel")
async def noop_handler() -> None:
    pass
