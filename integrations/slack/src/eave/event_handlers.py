import asyncio
import logging
import re
from typing import Optional

from slack_bolt.async_app import AsyncAck

import eave.eave_core as eave_core
import eave.openai_proxy as openai_proxy
import eave.slack_app as slack
from eave.document_manager import DocumentManager
from eave.json_object import JsonObject
from eave.settings import APP_SETTINGS
from eave.slack_models import SlackMessage

tasks = set[asyncio.Task]()


class WatchRequestEventHandler:
    async def handler(self, ack: AsyncAck, shortcut: Optional[JsonObject]) -> None:
        await ack()

        if shortcut is None:
            logging.warning("No shortcut passed in.")
            return

        message_json = shortcut.get("message")
        if message_json is None:
            return

        channel = shortcut["channel"]["id"]
        message = SlackMessage(message_json, channel=channel)

        task = asyncio.create_task(self.process_shortcut_message(message))
        tasks.add(task)
        task.add_done_callback(tasks.discard)

    async def process_shortcut_message(self, message: SlackMessage) -> None:
        eave_core_client = eave_core.EaveCoreClient()

        source = eave_core.SubscriptionSource(
            event=eave_core.SubscriptionSourceEvent.slack_message,
            id=message.subscription_id,
        )

        response = await eave_core_client.get_or_create_subscription(source=source)
        await message.add_reaction("eave")

        manager = DocumentManager(message=message, subscription=response.subscription)
        await manager.process_message()


class MessageEventHandler:
    async def handler(self, event: Optional[JsonObject]) -> None:
        logging.debug("received event: message")

        if event is None:
            logging.warning("No event present")
            return

        message = SlackMessage(event)
        task = asyncio.create_task(self.process_message(message))
        tasks.add(task)
        task.add_done_callback(tasks.discard)

    async def process_message(self, message: SlackMessage) -> None:
        logging.debug("process_message")

        if message.subtype in ["bot_message", "bot_remove", "bot_add"]:
            # Ignore messages from bots.
            # TODO: We should accept messages from bots
            logging.info("ignoring bot message")
            return

        if message.text is None:
            logging.warning("No message text")
            return

        if message.channel is None:
            logging.warning("No channel")
            return

        await message.get_expanded_text()
        eave_is_mentioned = any(
            profile.api_app_id == APP_SETTINGS.eave_slack_app_id for profile in message.user_mentions
        )

        if eave_is_mentioned:
            await message.add_reaction("eave")

        eave_core_client = eave_core.EaveCoreClient()

        if eave_is_mentioned and message.text_without_leading_mention is not None:
            question_match = re.match(f"^Question: (.+?\\?)", message.text_without_leading_mention)
            if question_match is not None:
                question = question_match.groups()[0]
                formatted_conversation = await message.get_formatted_conversation()
                prompt = (
                    "The following is a conversation between colleagues:\n"
                    f"{formatted_conversation}\n\n"
                    f"Answer the following question in the context of the above conversation:\n"
                    f"{question}"
                )

                answer = await openai_proxy.summarize(prompt=prompt)
                await slack.client.chat_postMessage(
                    channel=message.channel,
                    text=f"<@{message.user}> {answer}",
                    thread_ts=message.parent_ts,
                )
                return

        if not eave_is_mentioned:
            logging.info("Eave is not subscribed to this message; ignoring")
            return

        source = eave_core.SubscriptionSource(
            event=eave_core.SubscriptionSourceEvent.slack_message,
            id=message.subscription_id,
        )

        response = await eave_core_client.get_or_create_subscription(source=source)
        manager = DocumentManager(message=message, subscription=response.subscription)
        await manager.process_message()
