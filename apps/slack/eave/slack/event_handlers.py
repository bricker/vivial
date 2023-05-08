import json
import os
from typing import Optional

import eave.pubsub_schemas
import eave.slack.brain
import eave.slack.slack_models
import eave.stdlib
import eave.stdlib.core_api
import eave.stdlib.util as eave_util
from eave.slack.config import app_config
from eave.stdlib import logger
from slack_bolt.async_app import AsyncAck, AsyncApp, AsyncBoltContext

# TODO: Handlers create tasks for Cloud Tasks, or pubsub perhaps


def register_event_handlers(app: AsyncApp) -> None:
    app.shortcut("eave_watch_request")(shortcut_eave_watch_request_handler)
    app.event("message")(event_message_handler)
    app.event("app_mention")(noop_handler)
    app.event("reaction_added")(noop_handler)
    app.event("file_shared")(noop_handler)
    app.event("file_public")(noop_handler)
    app.event("file_deleted")(noop_handler)
    app.event("member_joined_channel")(event_member_joined_channel_handler)


async def shortcut_eave_watch_request_handler(
    ack: AsyncAck,
    shortcut: Optional[eave_util.JsonObject],
    context: AsyncBoltContext,
) -> None:
    logger.debug("WatchRequestEventHandler %s", shortcut)
    assert shortcut is not None

    eave_team = context.get("eave_team")
    assert eave_team is not None

    await ack()

    # Not supported currently
    return
    # message_json = shortcut.get("message")
    # assert message_json is not None

    # # TODO: Use Shortcut slack model, and get shortcut actor
    # channel = shortcut["channel"]["id"]
    # message = eave.slack.slack_models.SlackMessage(message_json, channel=channel)
    # b = eave.slack.brain.Brain(message=message, eave_team=context["eave_team"])
    # eave_util.do_in_background(b.process_shortcut_event())


async def event_message_handler(event: Optional[eave_util.JsonObject], context: AsyncBoltContext) -> None:
    logger.debug("MessageEventHandler %s", event)
    assert event is not None

    eave_team = context.get("eave_team")
    if not eave_team:
        logger.error(msg := "No eave team available in message handler.")
        raise AssertionError(msg)

    message = eave.slack.slack_models.SlackMessage(data=event, slack_context=context)

    if fixture_collection_enabled:
        save_fixture(event=event)

    if message.subtype in ["bot_message", "bot_remove", "bot_add"] or message.bot_id is not None:
        # Ignore messages from bots.
        # TODO: We should accept messages from bots
        logger.debug("ignoring bot message")
        return

    b = eave.slack.brain.Brain(message=message, slack_context=context, eave_team=eave_team)
    eave_util.do_in_background(b.process_message())


async def event_member_joined_channel_handler(event: Optional[eave_util.JsonObject], context: AsyncBoltContext) -> None:
    eave_team = context.get("eave_team")

    if not event or not (event.get("channel")) or not (user_id := event.get("user_id")):
        logger.error(msg := "member_joined_channel event received, but channel or user_id wasn't available.")
        raise AssertionError(msg)

    if user_id != context.bot_user_id:
        return

    if context.client:
        await context.client.chat_postMessage(
            channel=event["channel"],
            text=(
                msg := (
                    "Hello, I’m Eave! I can assist with any of your documentation needs. Simply tag me in threads you want documented, and I’ll take care of it."
                )
            ),
        )

        eave.stdlib.analytics.log_event(
            event_name="eave_sent_message",
            event_description="Eave sent a message",
            event_source="slack app",
            eave_team_id=eave_team.id if eave_team else None,
            opaque_params={
                "integration": eave.stdlib.core_api.enums.Integration.slack.value,
                "message_content": msg,
                "message_purpose": "introduction after joining a channel",
            },
        )
    else:
        logger.warning("No Slack client available in the Slack context.")

    eave.stdlib.analytics.log_event(
        event_name="eave_joined_slack_channel",
        event_description="Eave joined a slack channel",
        event_source="slack app",
        eave_team_id=eave_team.id if eave_team else None,
        opaque_params=None,
    )


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
