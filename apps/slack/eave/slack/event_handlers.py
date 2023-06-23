import json
from typing import Optional

from google.cloud.tasks import Queue

import eave.pubsub_schemas
from eave.slack.brain.core import Brain
import eave.slack.slack_models
import eave.stdlib.typing
import eave.stdlib.analytics
from eave.stdlib import task_queue
from eave.stdlib.core_api.models.integrations import Integration
from eave.stdlib.exceptions import SlackDataError, UnexpectedMissingValue
from slack_bolt.async_app import AsyncAck, AsyncApp, AsyncBoltContext
from .config import EAVE_CTX_KEY, SLACK_EVENT_QUEUE_NAME, TASK_EXECUTION_COUNT_CONTEXT_KEY, app_config

from eave.stdlib.logging import LogContext, eaveLogger


def register_event_handlers(app: AsyncApp) -> None:
    app.shortcut("eave_watch_request")(shortcut_eave_watch_request_handler)
    app.event("message")(event_message_handler)
    # app.event("app_mention")(noop_handler)
    # app.event("reaction_added")(noop_handler)
    # app.event("file_shared")(noop_handler)
    # app.event("file_public")(noop_handler)
    # app.event("file_deleted")(noop_handler)
    app.event("member_joined_channel")(event_member_joined_channel_handler)
    app.error(error_handler)


async def error_handler(error: Exception, context: AsyncBoltContext) -> None:
    """
    Called by slack bolt when an exception occurs when running the event handler.
    """
    eave_ctx = LogContext.wrap(context.get(EAVE_CTX_KEY))
    eaveLogger.error(error, eave_ctx)


async def shortcut_eave_watch_request_handler(
    shortcut: Optional[eave.stdlib.typing.JsonObject],
    context: AsyncBoltContext,
) -> None:
    eave_ctx = LogContext.wrap(context.get(EAVE_CTX_KEY))
    eaveLogger.debug("Received event: eave_watch_request (shortcut)", eave_ctx)

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
    eave_ctx = LogContext.wrap(context.get(EAVE_CTX_KEY))
    eaveLogger.debug("Received event: message", eave_ctx)
    if event is None:
        raise SlackDataError("event parameter is missing")

    eave_team = context.get("eave_team")
    if not eave_team:
        raise UnexpectedMissingValue("eave_team")

    message = eave.slack.slack_models.SlackMessage(data=event, slack_ctx=context, eave_ctx=eave_ctx)

    if message.subtype in ["bot_message", "bot_remove", "bot_add"] or message.bot_id is not None:
        # Ignore messages from bots.
        # TODO: We should accept messages from bots
        eaveLogger.debug("ignoring bot message", eave_ctx)
        return

    b = Brain(message=message, eave_team=eave_team, slack_ctx=context, eave_ctx=eave_ctx)

    try:
        await b.process_message()
    except Exception as e:
        if app_config.is_socketmode:
            # In socketmode, there is no task queue.
            await b.notify_failure(e)
            raise

        # The purpose of this catch block is so that Eave has the opportunity to warn the user that the request failed.
        # But we only want to do that after Cloud Tasks has retried the task a few times.
        queue = await task_queue.get_queue(SLACK_EVENT_QUEUE_NAME)

        max_attempts = queue.retry_config.max_attempts  # The total number of attempts allowed (this will be > 0)
        total_attempts = context.get(
            TASK_EXECUTION_COUNT_CONTEXT_KEY, 0
        )  # The number of times Cloud Tasks executed this task so far, excluding this one

        eave_ctx.set(
            {
                "queue": json.loads(Queue.to_json(queue)),
                "task": {
                    "max_attempts": max_attempts,
                    "total_attempts": total_attempts,
                },
            }
        )

        eaveLogger.debug(f"{SLACK_EVENT_QUEUE_NAME} task state", eave_ctx)

        # This is on purpose == instead of >=, because we only want to send this message once.
        # There is risk of this task being run more than the max attempts, and the execution count header
        # can be imprecise, depending on timing, so this is an attempt to mitigate that.
        if total_attempts == max_attempts:
            eaveLogger.warning("Max retries met. Eave will send a message that the request failed.", eave_ctx)
            await b.notify_failure(e)

        # Always re-raise, very important. Cloud Tasks will decide if it wants to try this task again, not the app.
        # This error will in turn be handled by the Slack Bolt middleware, which calls `error_handler`, which logs the error.
        raise


async def event_member_joined_channel_handler(
    event: Optional[eave.stdlib.typing.JsonObject], context: AsyncBoltContext
) -> None:
    eave_ctx = LogContext.wrap(context.get(EAVE_CTX_KEY))
    eaveLogger.debug("Received event: member_joined_channel", eave_ctx)

    eave_team = context.get("eave_team")

    if not event or not (event.get("channel")) or not (user_id := event.get("user")):
        raise SlackDataError("event channel or user")

    if user_id != context.bot_user_id:
        eaveLogger.debug("user_id != context.bot_user_id", eave_ctx)
        return

    if context.client:
        ref = f"<@{context.bot_user_id}>" if context.bot_user_id else "@Eave"

        message = (
            "Hey there, I’m Eave! I’m here to help with any of your documentation needs. Try the following:\n"
            f"  • Tag {ref} in a thread that you want documented\n"
            f"  • Tag {ref} in a message that includes GitHub links to document code\n"
            f"  • Tag {ref} to help look for existing documentation\n"
        )

        await context.client.chat_postMessage(
            channel=str(event["channel"]),
            text=message,
        )

        eave.stdlib.analytics.log_event(
            event_name="eave_sent_message",
            event_description="Eave sent a message",
            event_source="slack app",
            eave_team_id=eave_team.id if eave_team else None,
            opaque_params={
                "integration": Integration.slack.value,
                "message_content": message,
                "message_purpose": "introduction after joining a channel",
            },
            ctx=eave_ctx,
        )
    else:
        eaveLogger.warning("No Slack client available in the Slack context.", eave_ctx)

    eave.stdlib.analytics.log_event(
        event_name="eave_joined_slack_channel",
        event_description="Eave joined a slack channel",
        event_source="slack app",
        eave_team_id=eave_team.id if eave_team else None,
        ctx=eave_ctx,
    )


async def noop_handler(ack: AsyncAck) -> None:
    await ack()
