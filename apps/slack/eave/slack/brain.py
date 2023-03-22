import asyncio
import enum
import logging
import os
import re
import traceback
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

import eave.stdlib.core_api.client as eave_core_api_client
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.operations as eave_ops
import eave.stdlib.openai as eave_openai
import eave.stdlib.util as eave_util
import slack_sdk.models.blocks
import slack_sdk.models.blocks.basic_components
import slack_sdk.models.blocks.block_elements
import slack_sdk.web.async_client
import tiktoken

from . import slack_models
from .config import app_config
from .slack_app import client as slack_client

tokencoding = tiktoken.get_encoding("gpt2")

PROMPT_PREFIX = (
    "You are Eave, an AI documentation expert. "
    "Your job is to write, find, and organize robust, detailed documentation of this organization's information, decisions, projects, and procedures. "
    "You are responsible for the quality and integrity of this organization's documentation."
)
TONE_DIRECTION = "Your response should be in the form of a chat message: brief, casual, friendly, and may end with at most one of the following emojis: 🗒✏😎📝👩‍💻😄👍😀."


class MessagePurpose(enum.Enum):
    REQUEST = "REQUEST"
    QUESTION = "QUESTION"
    WATCH = "WATCH"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class RequestType(enum.Enum):
    CREATE_DOCUMENTATION = "CREATE_DOCUMENTATION"
    SEARCH_DOCUMENTATION = "SEARCH_DOCUMENTATION"
    UPDATE_DOCUMENTATION = "UPDATE_DOCUMENTATION"
    DELETE_DOCUMENTATION = "DELETE_DOCUMENTATION"
    WATCH = "WATCH"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class Brain:
    message: slack_models.SlackMessage
    subscription_source: eave_models.SubscriptionSource
    team_id: UUID

    def __init__(self, message: slack_models.SlackMessage) -> None:
        self.message = message
        # FIXME: Hardcoded ID
        self.team_id = UUID("3345217c-fb27-4422-a3fc-c404b49aff8c")
        # self.team = await eave_core_api_client.get_team(slack_org_id: xxx)

    async def process_message(self) -> None:
        i_am_mentioned = await self.message.check_eave_is_mentioned()
        if i_am_mentioned is True:
            """
            Eave is mentioned in this message.
            1. Acknowledge receipt of the message.
            1. If she's being asked for thread information, handle that and stop processing.
            1. Otherwise, send a preliminary response and continue processing.
            """
            await self.acknowledge_receipt()

            is_info_request = await self.message.check_is_info_request()
            if is_info_request is True:
                await self.send_message_info()
                return

        else:
            """
            Eave is not mentioned in this message.
            1. Lookup an existing subscription for this source.
            1. If she is not subscribed, then ignore the message and stop processing.
            1. Otherwise, continue processing.
            """
            subscription_response = await self.get_subscription()
            if subscription_response is None:
                logging.debug("Eave is not subscribed to this thread; ignoring.")
                return

        purpose = await self.determine_message_purpose()

        match purpose:
            case MessagePurpose.REQUEST:
                eave_util.do_in_background(self.process_request())
            case MessagePurpose.QUESTION:
                eave_util.do_in_background(self.process_question())
            case MessagePurpose.WATCH:
                eave_util.do_in_background(self.process_watch_request())
            case MessagePurpose.OTHER | MessagePurpose.UNKNOWN:
                eave_util.do_in_background(self.process_unknown_request())

    async def process_shortcut_event(self) -> None:
        await self.acknowledge_receipt()

        # source = eave_models.SubscriptionSource(
        #     event=eave_models.SubscriptionSourceEvent.slack_message,
        #     id=message.subscription_id,
        # )

        # response = await eave_models.client.get_or_create_subscription(source=source)
        # manager = DocumentManager(message=message, subscription=response.subscription)
        # await manager.process_message()

    """
    Intent Processors
    """

    async def process_request(self) -> None:
        expanded_text = await self.message.get_expanded_text()
        assert expanded_text is not None

        prompt = (
            f"{PROMPT_PREFIX}\n"
            f"If the following request is for you to create some documentation, say: {RequestType.CREATE_DOCUMENTATION.value}\n"
            f"If the request is for you to find or search for some documentation, say: {RequestType.SEARCH_DOCUMENTATION.value}\n"
            f"If the request is for you to update some documentation, say: {RequestType.UPDATE_DOCUMENTATION.value}\n"
            f"If the request is for you to delete or archive some documentation, say: {RequestType.DELETE_DOCUMENTATION.value}\n"
            f"If the request is for you to subscribe, listen, or watch a conversation, say: {RequestType.WATCH.value}\n"
            f"Otherwise, say: {RequestType.OTHER.value}"
            "\n\n###\n\n"
            f"Request: {expanded_text}\n\n"
            "Your Answer: "
        )

        await self.handle_request(prompt=prompt)

    async def process_question(self) -> None:
        expanded_text = await self.message.get_expanded_text()
        assert expanded_text is not None

        prompt = (
            f"{PROMPT_PREFIX}\n"
            f"If the following question is asking if you can create documentation, say: {RequestType.CREATE_DOCUMENTATION.value}\n"
            f"If the question is asking if you can search existing documentation, or asking if there is existing documentation, say: {RequestType.SEARCH_DOCUMENTATION.value}\n"
            f"If the question is asking if you to can update some documentation, say: {RequestType.UPDATE_DOCUMENTATION.value}\n"
            f"If the question is asking if you can delete or archive some documentation, say: {RequestType.DELETE_DOCUMENTATION.value}\n"
            f"If the question is asking if you can subscribe, listen, or watch a conversation, say: {RequestType.WATCH.value}\n"
            f"Otherwise, say: {RequestType.OTHER.value}"
            "\n\n###\n\n"
            f"Question: {expanded_text}\n\n"
            "Your Response: "
        )

        await self.handle_request(prompt=prompt)

    async def process_watch_request(self) -> None:
        """
        Subscribes to the thread and creates initial documentation if not already subscribed,
        otherwise notifies the user that I'm already watching this conversation.
        """
        existing_subscription = await self.get_subscription()

        if existing_subscription is None:
            await self.respond_to_message(
                text=(
                    "Acknowledged! Because you tagged me, I'll continuously watch this conversation and document the information. "
                    "I'll get started on the initial documentation right away and send an update when it's ready."
                )
            )
            await self.create_subscription()
            await self.create_documentation()
            return
        else:
            await self.notify_existing_subscription(subscription=existing_subscription)
            return

    async def process_unknown_request(self) -> None:
        """
        Processes a request that wasn't recognized.
        Basically lets the user know that I wasn't able to process the message, and reminds them if I'm already documenting this conversation.
        """
        subscription = await self.get_subscription()

        if subscription is None:
            await self.respond_to_message(
                text=(
                    "Hey! I haven't been trained on how to respond to your message. I've let my development team know about it. "
                    f"Do you want me to watch and document this conversation? (This feature is not yet implemented) "
                    "If you needed something else, try phrasing it differently."
                )
            )

            # TODO: handle the response to this, eg if the user says "Yes please" or "No thanks"

        elif subscription.document_reference is not None:
            await self.respond_to_message(
                text=(
                    "Hey! I haven't been trained on how to respond to your message. I've let my development team know about it. "
                    "As a reminder, I'm watching this conversation and documenting the information <{subscription.document_reference.document_url}|here>. "
                    "If you needed something else, try phrasing it differently."
                )
            )

        else:
            await self.respond_to_message(
                text=(
                    "Hey! I haven't been trained on how to respond to your message. I've let my development team know about it. "
                    f"I'm currently working on the documentation for this conversation, and I'll send an update when it's ready. "
                    "If you needed something else, try phrasing it differently."
                )
            )

    @eave_util.memoized
    async def determine_message_purpose(self) -> MessagePurpose:
        """
        Asks OpenAI to determine why the user mentioned Eave.
        For example, the user may have mentioned Eave because they are requesting specific documentation,
        or they may just be tagging Eave to watch the conversation.
        """
        expanded_text = await self.message.get_expanded_text()
        assert expanded_text is not None

        prompt = (
            f"{PROMPT_PREFIX}\n"
            f"If the following message is requesting something from you, or asking you to do something that you are able to do, say: {MessagePurpose.REQUEST.value}\n"
            f"If the message is asking you another type of question, say: {MessagePurpose.QUESTION.value}\n"
            f"If the message is simply notifying or tagging you, say: {MessagePurpose.WATCH.value}\n"
            f"Otherwise, say: {MessagePurpose.OTHER.value}"
            "\n\n###\n\n"
            f"Message: {expanded_text}\n\n"
            "Response: "
        )

        openai_response = await self.get_openai_response(prompt=prompt, temperature=0)

        try:
            purpose = MessagePurpose(value=self.normalize_for_enum(openai_response))
        except ValueError as e:
            logging.exception(f"Unexpected purpose response", exc_info=e, extra={"response": openai_response})
            purpose = MessagePurpose.UNKNOWN

        return purpose

    async def handle_request(self, prompt: str) -> None:
        """
        Determines the RequestType, and then handles the message accordingly.
        """

        openai_response = await self.get_openai_response(prompt=prompt, temperature=0)

        try:
            request_type = RequestType(value=self.normalize_for_enum(openai_response))
        except ValueError as e:
            logging.exception(f"Unexpected request type response", exc_info=e, extra={"response": openai_response})
            request_type = RequestType.UNKNOWN

        match request_type:
            case RequestType.CREATE_DOCUMENTATION:
                existing_subscription = await self.get_subscription()
                if existing_subscription is None:
                    await self.respond_to_message(
                        text=("Sure! I'll work on this now and send an update when it's ready.")
                    )
                    await self.create_subscription()
                    await self.create_documentation()
                else:
                    await self.notify_existing_subscription(subscription=existing_subscription)

                return

            case RequestType.SEARCH_DOCUMENTATION:
                await self.respond_to_message(text="One moment while I look...")
                await self.search_documentation()
                return

            case RequestType.UPDATE_DOCUMENTATION:
                await self.respond_to_message(text="On it!")
                await self.update_documentation()
                return

            case RequestType.DELETE_DOCUMENTATION:
                # TODO: Unsubscribe from conversation
                await self.respond_to_message(text="On it!")
                await self.archive_documentation()
                return

            case RequestType.WATCH:
                await self.process_watch_request()
                return

            case RequestType.OTHER | RequestType.UNKNOWN:
                await self.process_unknown_request()
                return

    """
    Document Management
    """

    async def create_documentation(self) -> None:
        """
        A procedure to execute the following tasks:
        1. Generate documentation from the conversation
        2. Parse the generated documentation and add contextual information
        3. Send the final document to Core API (i.e. save the document to the organization's documentation destination)
        4. Send a follow-up response to the original Slack thread with a link to the documentation
        """

        async def get_raw_documentation() -> str:
            """
            Sends the conversation to OpenAI and asks for documentation.
            If the user requested something specific (instead of simply tagging Eave), that user prompt is also sent to
            OpenAI.
            """
            context = await self.build_context()

            prompt = (
                f"{PROMPT_PREFIX}\n"
                "Generate a category, title, and formatted documentation for the information in this conversation. "
                "Example categories: Engineering, Product, Marketing, Website, Design\n\n"
            )

            prompt += (
                "Desired Format:\n"
                "CATEGORY: -||-\n"
                "TITLE: -||-\n"
                "FORMATTED DOCUMENTATION: -||-"
                "\n\n###\n\n"
                f"{context}\n\n"
                "CATEGORY: "
            )

            openai_params = eave_openai.CompletionParameters(
                prompt=prompt,
                n=1,
                frequency_penalty=0.6,
                presence_penalty=0.3,
                temperature=0.2,
            )

            openai_response = await eave_openai.completion(openai_params)
            assert openai_response is not None
            return openai_response

        initial_generated_documentation = await get_raw_documentation()

        # async def get_document_metadata() -> str:
        #     prompt = (
        #         f"{PROMPT_PREFIX}\n"
        #         "Extract a project name and documentation type of the following documentation.\n\n"
        #         "Desired Format:\n"
        #         "PROJECT NAME: -||-\n"
        #         "DOCUMENTATION TYPE: -||-\n"
        #     )
        #     openai_params = eave_openai.CompletionParameters(
        #         prompt=prompt,
        #         n=1,
        #         frequency_penalty=0.6,
        #         presence_penalty=0.3,
        #         temperature=0.2,
        #     )

        #     openai_response = await eave_openai.summarize(openai_params)
        #     assert openai_response is not None
        #     return openai_response

        # document_metadata = await get_document_metadata()

        # tokens = tokencoding.encode(response)
        # truncated_content = ""
        # openai_params = eave_openai.CompletionParameters(
        #     prompt=f"Create a title for this document.\n\n###\n\n{content}\n\nTitle:\n",
        #     n=1,
        #     frequency_penalty=0,
        #     temperature=0.2,
        # )
        # title = await eave_openai.summarize(openai_params)
        # assert title is not None

        async def parse_raw_documentation() -> eave_ops.DocumentInput:
            """
            1. Parses the OpenAI response. Makes assumptions about the format of the text returned by OpenAI.
            2. Adds context to the document (eg links and source)
            """
            category, title, body = initial_generated_documentation.split("\n", maxsplit=2)
            category = category.strip()
            title = re.sub("^TITLE:\\s*", "", title, flags=re.RegexFlag.IGNORECASE).strip()
            body = re.sub("^FORMATTED DOCUMENTATION:\\s*", "", body, flags=re.RegexFlag.IGNORECASE).strip()

            generated_document = eave_ops.DocumentInput(
                title=title,
                content=body,
                parent=eave_ops.DocumentInput(
                    title=category,
                    content="",
                ),
            )

            all_messages = await self.message.get_conversation_messages()
            assert all_messages is not None

            [await message.get_expanded_text() for message in all_messages]
            # TODO: Remove duplicate URLs
            links = [link for message in all_messages for link in message.urls]

            if len(links) > 0:
                generated_document.content += "\n\nh3. Resources\n\n"
                for link in links:
                    parts = link.split("|")
                    if len(parts) > 1:
                        # Slack formats links as [URL|Name], but Confluence wants them formatted as [Name|URL].
                        # This line swaps them.
                        generated_document.content += f"- [{parts[1]}|{parts[0]}]\n"
                    else:
                        generated_document.content += f"- [{parts[0]}]\n"

            generated_document.content += "\n\nh3. Source\n\n"
            permalink = await self.message.get_parent_permalink()
            if permalink is not None:
                doc_source = str(permalink.permalink)
                generated_document.content += f"[Slack|{doc_source}]"
            else:
                doc_source = f"Slack message: {self.message.subscription_id}"

            return generated_document

        document = await parse_raw_documentation()

        upsert_document_response = await eave_core_api_client.upsert_document(
            team_id=self.team_id,
            input=eave_ops.UpsertDocument.RequestBody(
                subscription=eave_ops.SubscriptionInput(source=self.message.subscription_source),
                document=document,
            ),
        )

        async def send_follow_up_message() -> None:
            """
            Generated a nice message and sends it back to the original Slack thread, along with a link to the new documentation.
            """
            slack_profile = await self.message.get_user_profile()
            assert slack_profile is not None

            message = f"Here's the documentation that you asked for! I'll keep it up-to-date and accurate."

            await self.respond_to_message(
                text=f"{message}\n<{upsert_document_response.document_reference.document_url}|{document.title}>"
            )

        await send_follow_up_message()

    async def search_documentation(self) -> None:
        # blocks = [
        #     slack_sdk.models.blocks.SectionBlock(
        #         text=slack_sdk.models.blocks.basic_components.MarkdownTextObject(
        #             text=f"*<{document_reference.document_url}|{document.title}>*\n{document.summary}",
        #         ),
        #     ),
        #     slack_sdk.models.blocks.DividerBlock(),
        #     slack_sdk.models.blocks.SectionBlock(
        #         text=slack_sdk.models.blocks.basic_components.MarkdownTextObject(
        #             text=f"*<{document_reference.document_url}|{document.title}>*\n{document.summary}",
        #         ),
        #     ),
        #     slack_sdk.models.blocks.DividerBlock(),
        #     slack_sdk.models.blocks.SectionBlock(
        #         text=slack_sdk.models.blocks.basic_components.MarkdownTextObject(
        #             text=f"*<{document_reference.document_url}|{document.title}>*\n{document.summary}",
        #         ),
        #     ),
        #     slack_sdk.models.blocks.DividerBlock(),
        #     slack_sdk.models.blocks.ActionsBlock(
        #         elements=[
        #             slack_sdk.models.blocks.block_elements.ButtonElement(
        #                 text="Load more results (noop)",
        #             ),
        #         ],
        #     ),
        # ]
        # await self.respond_to_message(blocks=blocks)

        await self.respond_to_message(text="I haven't yet been taught how to search existing documentation.")

    async def update_documentation(self) -> None:
        await self.respond_to_message(text="I haven't yet been taught how to update existing documentation.")

    async def archive_documentation(self) -> None:
        await self.respond_to_message(text="I haven't yet been taught how to archive existing documentation.")

    """
    Context Building
    """

    async def build_context(self) -> str:
        context = await self.build_concatenated_context()
        if len(tokencoding.encode(context)) > (eave_openai.MAX_TOKENS / 2):
            context = await self.build_rolling_context()

        return context

    async def build_concatenated_context(self) -> str:
        messages = await self.message.get_conversation_messages()
        assert messages is not None

        messages_without_self = filter(lambda m: m.is_eave is False, messages)

        formatted_messages: list[Optional[str]] = await asyncio.gather(
            *[message.simple_format() for message in messages_without_self]
        )

        filtered_messages = filter(None, formatted_messages)
        formatted_conversation = "\n".join(filtered_messages)

        # TODO: Add in reactions
        return formatted_conversation

    async def build_rolling_context(self) -> str:
        messages = await self.message.get_conversation_messages()
        assert messages is not None

        messages_without_self = filter(lambda m: m.is_eave is False, messages)

        messages_for_prompt = list[str]()
        total_tokens = 0

        condensed_context = ""

        for thread_message in messages_without_self:
            formatted_text = await thread_message.simple_format()
            if formatted_text is None:
                continue

            tokens = tokencoding.encode(formatted_text)
            total_tokens += len(tokens)

            if total_tokens > (eave_openai.MAX_TOKENS / 2):
                joined_messages = "\n\n".join(messages_for_prompt)
                prompt = (
                    f"{PROMPT_PREFIX}\n"
                    "Condense the following conversation. Maintain the important information."
                    "\n\n###\n\n"
                    f"{condensed_context}\n\n"
                    f"{joined_messages}\n\n"
                )
                openai_params = eave_openai.CompletionParameters(
                    prompt=prompt,
                    temperature=0.9,
                    frequency_penalty=1.0,
                    presence_penalty=1.0,
                )
                response = await eave_openai.completion(params=openai_params)
                assert response is not None
                condensed_context = response
                total_tokens = 0
                messages_for_prompt.clear()

            messages_for_prompt.append(formatted_text)

        recent_messages = "\n\n".join(messages_for_prompt)
        return f"{condensed_context}\n\n" f"{recent_messages}"

    """
    Utility
    """

    @staticmethod
    def normalize_for_enum(value: str) -> str:
        return re.sub(pattern="\\W", repl="", string=value).upper()

    async def respond_to_message(
        self, text: Optional[str] = None, blocks: Optional[List[slack_sdk.models.blocks.Block]] = None
    ) -> None:
        assert self.message.channel is not None

        debug_text = ""
        if app_config.dev_mode is True:
            stack = traceback.extract_stack(limit=2)
            frame = stack[0]
            filename = os.path.basename(frame.filename)
            formatted_frame = f"{filename}:{frame.lineno}"
            debug_text = f" ({formatted_frame})"

        if text is not None:
            msg = f"<@{self.message.user}> {text}{debug_text}"

            await slack_client.chat_postMessage(
                channel=self.message.channel,
                text=msg,
                thread_ts=self.message.parent_ts,
            )
            return

    #         if blocks is not None:
    #             blocks.extend([
    #                 slack_sdk.models.blocks.DividerBlock(),
    #                 slack_sdk.models.blocks.ContextBlock(
    #                     elements=[
    # slack_sdk.models.blocks.basic_components.MarkdownTextObject(
    #                         text=f"*<{document_reference.document_url}|{document.title}>*\n{document.summary}",
    #                     ),
    #                     ]
    #                     text=
    #                 ),
    #             ])
    #             await eave.slack.client.chat_postMessage(
    #                 channel=self.message.channel,
    #                 blocks=blocks,
    #                 thread_ts=self.message.parent_ts,
    #             )
    #             return

    async def react_to_message(self, name: str) -> None:
        assert self.message.channel is not None
        assert self.message.ts is not None
        await slack_client.reactions_add(name=name, channel=self.message.channel, timestamp=self.message.ts)

    async def acknowledge_receipt(self) -> None:
        await self.react_to_message("eave")

    async def send_message_info(self) -> None:
        info = f"Subscription ID: {self.message.subscription_id}"
        await self.respond_to_message(text=info)

    async def get_openai_response(self, prompt: str, temperature: int) -> str:
        params = eave_openai.CompletionParameters(
            prompt=prompt,
            temperature=temperature,
        )

        openai_completion = await eave_openai.completion(params)
        assert openai_completion is not None
        return openai_completion

    async def get_subscription(self) -> eave_ops.GetSubscription.ResponseBody | None:
        subscription = await eave_core_api_client.get_subscription(
            team_id=self.team_id,
            input=eave_ops.GetSubscription.RequestBody(
                subscription=eave_ops.SubscriptionInput(source=self.message.subscription_source),
            ),
        )
        return subscription

    async def create_subscription(self) -> eave_ops.CreateSubscription.ResponseBody:
        """
        Gets and returns the subscription if it already exists, otherwise creates and returns a new subscription.
        """
        subscription = await eave_core_api_client.create_subscription(
            team_id=self.team_id,
            input=eave_ops.CreateSubscription.RequestBody(
                subscription=eave_ops.SubscriptionInput(source=self.message.subscription_source),
            ),
        )
        return subscription

    async def notify_existing_subscription(self, subscription: eave_ops.GetSubscription.ResponseBody) -> None:
        if subscription.document_reference is not None:
            await self.respond_to_message(
                text=(
                    f"Hey! I'm already watching this conversation and documenting the information <{subscription.document_reference.document_url}|here>. "
                    "Let me know if you need anything else!"
                )
            )
            return

        else:
            await self.respond_to_message(
                text=(
                    f"Hey! I'm currently working on the documentation for this conversation. I'll send an update when it's ready."
                )
            )
            return
