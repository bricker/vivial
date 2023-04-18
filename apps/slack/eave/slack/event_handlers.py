import json
import os
from typing import Optional

import eave.slack.brain
import eave.slack.slack_models
import eave.stdlib.util as eave_util
import eave.stdlib.core_api.client as eave_core
from eave.slack.config import app_config
from eave.stdlib import logger
from slack_bolt.async_app import AsyncAck, AsyncApp, AsyncBoltContext


def register_event_handlers(app: AsyncApp) -> None:
    app.shortcut("eave_watch_request")(shortcut_eave_watch_request_handler)
    app.event("message")(event_message_handler)
    app.event("app_mention")(noop_handler)
    app.event("reaction_added")(noop_handler)
    app.event("file_shared")(noop_handler)
    app.event("file_public")(noop_handler)
    app.event("file_deleted")(noop_handler)
    app.event("member_joined_channel")(noop_handler)


async def shortcut_eave_watch_request_handler(ack: AsyncAck, shortcut: Optional[eave_util.JsonObject], context: AsyncBoltContext) -> None:
    logger.debug("WatchRequestEventHandler %s", shortcut)
    await ack()
    assert shortcut is not None

    message_json = shortcut.get("message")
    assert message_json is not None

    # TODO: Use Shortcut slack model, and get shortcut actor
    channel = shortcut["channel"]["id"]
    message = eave.slack.slack_models.SlackMessage(message_json, channel=channel)
    b = eave.slack.brain.Brain(message=message, eave_team=context["eave_team"])
    eave_util.do_in_background(b.process_shortcut_event())


async def event_message_handler(event: Optional[eave_util.JsonObject], context: AsyncBoltContext) -> None:
    logger.debug("MessageEventHandler %s", event)
    assert event is not None

    message = eave.slack.slack_models.SlackMessage(event)

    if fixture_collection_enabled:
        save_fixture(event=event)

    if message.subtype in ["bot_message", "bot_remove", "bot_add"]:
        # Ignore messages from bots.
        # TODO: We should accept messages from bots
        logger.debug("ignoring bot message")
        return

    b = eave.slack.brain.Brain(message=message, eave_team=context["eave_team"])
    eave_util.do_in_background(b.process_message())


async def noop_handler() -> None:
    pass


fixture_collection_enabled = (
    app_config.dev_mode and os.getenv("SLACK_SOCKETMODE") is not None and os.getenv("FIXTURE_COLLECTION") is not None
)


def save_fixture(event: eave_util.JsonObject) -> None:
    os.makedirs(".event_fixtures/message", exist_ok=True)

    fn = event["ts"]
    with open(f".event_fixtures/message/{fn}.json", mode="w") as f:
        f.write(json.dumps(event, indent=2, sort_keys=True))
