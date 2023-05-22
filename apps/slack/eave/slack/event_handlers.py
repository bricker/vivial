from typing import Optional

import eave.pubsub_schemas
import eave.slack.brain
import eave.slack.slack_models
from eave.slack.util import log_context
import eave.stdlib
from eave.stdlib import task_queue
import eave.stdlib.core_api
from eave.stdlib.exceptions import SlackDataError, UnexpectedMissingValue
from slack_bolt.async_app import AsyncAck, AsyncApp, AsyncBoltContext
from .config import SLACK_EVENT_QUEUE_NAME, TASK_EXECUTION_COUNT_CONTEXT_KEY, app_config

from eave.stdlib.logging import eaveLogger


def register_event_handlers(app: AsyncApp) -> None:
    app.shortcut("eave_watch_request")(shortcut_eave_watch_request_handler)
    app.event("message")(event_message_handler)
    # app.event("app_mention")(noop_handler)
    # app.event("reaction_added")(noop_handler)
    # app.event("file_shared")(noop_handler)
    # app.event("file_public")(noop_handler)
    # app.event("file_deleted")(noop_handler)
    app.event("member_joined_channel")(event_member_joined_channel_handler)


async def shortcut_eave_watch_request_handler(
    shortcut: Optional[eave.stdlib.typing.JsonObject],
    context: AsyncBoltContext,
) -> None:
    eaveLogger.debug("Received event: eave_watch_request (shortcut)", extra=log_context(context))
    if shortcut is None:
        raise SlackDataError("shortcut parameter")

    eave_team = context.get("eave_team")
    if eave_team is None:
        raise UnexpectedMissingValue("slack shortcut eave team")

    # Not supported currently
    return
    # message_json = shortcut.get("message")
    # assert message_json is not None

    # # TODO: Use Shortcut slack model, and get shortcut actor
    # channel = shortcut["channel"]["id"]
    # message = eave.slack.slack_models.SlackMessage(message_json, channel=channel)
    # b = eave.slack.brain.Brain(message=message, eave_team=context["eave_team"])
    # eave_util.do_in_background(b.process_shortcut_event())


async def event_message_handler(event: Optional[eave.stdlib.typing.JsonObject], context: AsyncBoltContext) -> None:
    extra = log_context(context)
    eaveLogger.debug("Received event: message", extra=extra)
    if event is None:
        raise SlackDataError("event parameter")

    eave_team = context.get("eave_team")
    if not eave_team:
        raise UnexpectedMissingValue("slack event eave team")

    message = eave.slack.slack_models.SlackMessage(data=event, slack_context=context)

    if message.subtype in ["bot_message", "bot_remove", "bot_add"] or message.bot_id is not None:
        # Ignore messages from bots.
        # TODO: We should accept messages from bots
        eaveLogger.debug("ignoring bot message", extra=extra)
        return

    b = eave.slack.brain.Brain(message=message, eave_team=eave_team)

    try:
        await b.process_message()
    except Exception as e:
        if app_config.is_socketmode:
            # In socketmode, there is no task queue.
            await b.notify_failure(e)
            raise

        # Assume that the exception was already logged.
        # The purpose of this catch block is so that Eave has the opportunity to warn the user that the request failed.
        # But we only want to do that after Cloud Tasks has retried the task a few times.
        queue = await task_queue.get_queue(SLACK_EVENT_QUEUE_NAME)

        max_attempts = queue.retry_config.max_attempts  # The total number of attempts allowed (this will be > 0)
        total_attempts = context.get(
            TASK_EXECUTION_COUNT_CONTEXT_KEY, 0
        )  # The number of times Cloud Tasks executed this tasks so far, excluding this one

        # This is on purpose == instead of >=, because we only want to send this message once.
        # There is risk of this task being run more than the max attempts, and the execution count header
        # can be imprecise, depending on timing, so this is an attempt to mitigate that.
        if total_attempts == max_attempts:
            eaveLogger.warning("Max retries met. Eave will send a message that the request failed.")
            await b.notify_failure(e)

        # Always re-raise, very important
        raise


async def event_member_joined_channel_handler(
    event: Optional[eave.stdlib.typing.JsonObject], context: AsyncBoltContext
) -> None:
    extra = log_context(context)
    eaveLogger.debug("Received event: member_joined_channel", extra=extra)

    eave_team = context.get("eave_team")

    if not event or not (event.get("channel")) or not (user_id := event.get("user")):
        raise SlackDataError("event channel or user")

    if user_id != context.bot_user_id:
        eaveLogger.debug("user_id != context.bot_user_id", extra=extra)
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
        eaveLogger.warning("No Slack client available in the Slack context.", extra=extra)

    eave.stdlib.analytics.log_event(
        event_name="eave_joined_slack_channel",
        event_description="Eave joined a slack channel",
        event_source="slack app",
        eave_team_id=eave_team.id if eave_team else None,
        opaque_params=None,
    )


async def noop_handler(ack: AsyncAck) -> None:
    await ack()
