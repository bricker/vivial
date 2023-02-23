import asyncio
import logging
from typing import Optional

from slack_bolt.async_app import AsyncAck

import eave.brain
import eave.slack_models
import eave.util


class WatchRequestEventHandler:
    @staticmethod
    async def handler(ack: AsyncAck, shortcut: Optional[eave.util.JsonObject]) -> None:
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


class MessageEventHandler:
    @staticmethod
    async def handler(event: Optional[eave.util.JsonObject]) -> None:
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


class NoopEventHandler:
    @staticmethod
    async def handler() -> None:
        pass
