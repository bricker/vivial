import asyncio
from dataclasses import dataclass
import enum
import logging
import os
import re
import traceback
from typing import Optional

import tiktoken
import eave.slack_models
import eave.openai
import eave.slack
import eave.core_api
import eave.util
import eave.settings

tokencoding = tiktoken.get_encoding("gpt2")

PROMPT_PREFIX = (
    "You are Eave, an AI documentation expert. "
    "Your job is to write, find, and organize robust, detailed documentation of this organization's information, decisions, projects, and procedures. "
    "You are responsible for the quality and integrity of this organization's documentation."
)
TONE_DIRECTION = (
    "Your response should be in the form of a chat message: brief, casual, friendly, and may end with at most one of the following emojis: 🗒✏😎📝👩‍💻😄👍😀."
)

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

@dataclass
class GeneratedDocument:
    title: str
    content: str
    bucket: Optional[str]
    # category: Optional[str]
    # topics: list[str]

class Brain:
    message: eave.slack_models.SlackMessage
    subscription_source: eave.core_api.SubscriptionSource

    def __init__(self, message: eave.slack_models.SlackMessage) -> None:
        self.message = message
        self.subscription_source = eave.core_api.SubscriptionSource(
            event=eave.core_api.SubscriptionSourceEvent.slack_message,
            id=message.subscription_id
        )

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

            await self.send_preliminary_response()
        else:
            """
            Eave is not mentioned in this message.
            1. Lookup an existing subscription for this source.
            1. If she is not subscribed, then ignore the message and stop processing.
            1. Otherwise, continue processing.
            """
            subscription_response = await eave.core_api.client.get_subscription(source=self.subscription_source)
            if subscription_response is None:
                logging.debug("Eave is not subscribed to this thread; ignoring.")
                return

        purpose = await self.determine_message_purpose()

        match purpose:
            case MessagePurpose.REQUEST:
                eave.util.do_in_background(self.process_request())
            case MessagePurpose.QUESTION:
                eave.util.do_in_background(self.process_question())
            case MessagePurpose.WATCH:
                eave.util.do_in_background(self.process_watch_request())
            case MessagePurpose.OTHER | MessagePurpose.UNKNOWN:
                logging.warning(f"Unexpected message purpose: {purpose}")


    async def process_shortcut_event(self) -> None:
        await self.acknowledge_receipt()

        # source = eave.core_api.SubscriptionSource(
        #     event=eave.core_api.SubscriptionSourceEvent.slack_message,
        #     id=message.subscription_id,
        # )

        # response = await eave.core_api.client.get_or_create_subscription(source=source)
        # manager = DocumentManager(message=message, subscription=response.subscription)
        # await manager.process_message()

    async def send_preliminary_response(self) -> None:
        """
        Generates and sends an acknowledgement to the initial user-provided prompt.

        The prompt to OpenAI depends on the nature ("purpose") of the user-provided prompt.

        The goal is to provide the user some quick feedback that the message has been received, while we process it in
        the background. `acknowledge`
        """
        purpose = await self.determine_message_purpose()
        expanded_text = await self.message.get_expanded_text()
        assert expanded_text is not None

        # TODO: include conversation context in the prompts
        match purpose:
            case MessagePurpose.REQUEST:
                prompt = (
                    f"{PROMPT_PREFIX}\n"
                    "You were called on to handle the following request. "
                    "Say that you'll work on it, and will send an update when it's completed. "
                    f"{TONE_DIRECTION}"
                    "\n\n###\n\n"
                    f"Request: {expanded_text}\n\n"
                    "Response: "
                )

            case MessagePurpose.QUESTION:
                prompt = (
                    f"{PROMPT_PREFIX}\n"
                    f"You were asked the following question. "
                    "If you're able to answer the question with high confidence, go ahead and answer it. "
                    "It is important that you only answer the question if you are confident in the answer. "
                    "Otherwise, say that you'll look into it, and will send an update when you have the answer. "
                    f"{TONE_DIRECTION}"
                    "\n\n###\n\n"
                    f"Question: {expanded_text}\n\n"
                    "Response: "
                )

            case MessagePurpose.WATCH:
                prompt = (
                    f"{PROMPT_PREFIX}\n"
                    "You were told to keep an eye on this conversation and document the details. "
                    "Say that you'll document this conversation and will send a link when it's ready. "
                    f"{TONE_DIRECTION}"
                    "\n\n###\n\n"
                )

            case MessagePurpose.OTHER | MessagePurpose.UNKNOWN:
                prompt = (
                    f"{PROMPT_PREFIX}\n"
                    "Write a response to the following message, and ask if you should watch this conversation and document this information. "
                    "In parentheses, make it clear that this feature isn't implemented yet, and that this is just a demonstration. "
                    f"{TONE_DIRECTION}"
                    "\n\n###\n\n"
                    f"Message: {expanded_text}\n\n"
                    "Response: "
                )
                # TODO: handle the response to this, eg if the user says "Yes please" or "No thanks"

        params = eave.openai.CompletionParameters(
            prompt=prompt,
            temperature=0,
        )

        openai_completion = await eave.openai.summarize(params)
        assert openai_completion is not None
        await self.respond_to_message(text=openai_completion, caller_id=f"send_preliminary_response:{purpose.value}")


    """
    Intent Processors
    """

    async def process_request(self) -> None:
        expanded_text = await self.message.get_expanded_text()
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
            "Answer: "
        )

        params = eave.openai.CompletionParameters(
            prompt=prompt,
            temperature=0,
        )

        response = await eave.openai.summarize(params)
        assert response is not None

        try:
            purpose = RequestType(value=self.normalize_for_enum(response))
        except ValueError as e:
            logging.exception(f"Unexpected purpose response", exc_info=e, extra={"response":response})
            purpose = RequestType.UNKNOWN

        match purpose:
            case RequestType.CREATE_DOCUMENTATION:
                await self.subscribe_to_conversation()
                await self.create_documentation(user_provided_prompt=expanded_text)
            case RequestType.SEARCH_DOCUMENTATION:
                await self.search_documentation()
            case RequestType.UPDATE_DOCUMENTATION:
                await self.subscribe_to_conversation()
                await self.update_documentation()
            case RequestType.DELETE_DOCUMENTATION:
                # TODO: Unsubscribe from conversation
                await self.archive_documentation()
            case RequestType.WATCH:
                await self.subscribe_to_conversation()
                await self.create_documentation()
            case RequestType.OTHER | RequestType.UNKNOWN:
                await self.respond_to_message(text="I haven't yet been taught how to handle this request.", caller_id=f"process_request:{purpose.value}")

    async def process_question(self) -> None:
        expanded_text = await self.message.get_expanded_text()
        prompt = (
            f"{PROMPT_PREFIX}\n"
            f"If the following question is asking for new documentation, say: {RequestType.CREATE_DOCUMENTATION.value}\n"
            f"If the question is asking you to search existing documentation, say: {RequestType.SEARCH_DOCUMENTATION.value}\n"
            f"If the question is asking you to update some documentation, say: {RequestType.UPDATE_DOCUMENTATION.value}\n"
            f"If the question is asking you to delete or archive some documentation, say: {RequestType.DELETE_DOCUMENTATION.value}\n"
            f"If the question is asking you to subscribe, listen, or watch a conversation, say: {RequestType.WATCH.value}\n"
            f"Otherwise, say: {RequestType.OTHER.value}"
            "\n\n###\n\n"
            f"Question: {expanded_text}\n\n"
            "Answer: "
        )

        params = eave.openai.CompletionParameters(
            prompt=prompt,
            temperature=0,
        )

        response = await eave.openai.summarize(params)
        assert response is not None

        try:
            purpose = RequestType(value=self.normalize_for_enum(response))
        except ValueError as e:
            logging.exception(f"Unexpected purpose response", exc_info=e, extra={"response":response})
            purpose = RequestType.UNKNOWN

        match purpose:
            case RequestType.CREATE_DOCUMENTATION:
                await self.subscribe_to_conversation()
                await self.create_documentation(user_provided_prompt=expanded_text)
            case RequestType.SEARCH_DOCUMENTATION:
                await self.search_documentation()
            case RequestType.UPDATE_DOCUMENTATION:
                await self.subscribe_to_conversation()
                await self.update_documentation()
            case RequestType.DELETE_DOCUMENTATION:
                # TODO: Unsubscribe from conversation
                await self.archive_documentation()
            case RequestType.WATCH:
                await self.subscribe_to_conversation()
                await self.create_documentation()
            case RequestType.OTHER | RequestType.UNKNOWN:
                await self.respond_to_message(text="I haven't yet been taught how to handle this request.")

    async def process_watch_request(self) -> None:
        """
        Subscribes to the thread if not already subscribed, and then either creates or updates the documentation.
        """
        # FIXME: subscribe_to_conversation is a noop if Eave is already subscribed; function should be renamed
        await self.subscribe_to_conversation()

        # FIXME: If Eave is already subscribed to this conversation, this actually updates the document; function should be renamed.
        await self.create_documentation()


    async def subscribe_to_conversation(self) -> None:
        """
        If Eave is not already subscribed to this conversation:
        1. Subscribes to the conversation
        2. Generates initial documentation
        """
        await eave.core_api.client.get_or_create_subscription(source=self.subscription_source)

    @eave.util.memoized
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

        params = eave.openai.CompletionParameters(
            prompt=prompt,
            temperature=0,
        )

        response = await eave.openai.summarize(params)
        assert response is not None

        try:
            purpose = MessagePurpose(value=self.normalize_for_enum(response))
            return purpose
        except ValueError as e:
            logging.exception(f"Unexpected purpose response", exc_info=e, extra={"response":response})
            return MessagePurpose.UNKNOWN

    """
    Document Management
    """

    async def create_documentation(self, user_provided_prompt: Optional[str]=None) -> None:
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
                "Generate a bucket name, title, and formatted documentation for the information in this conversation. "
            )

            if user_provided_prompt is not None:
                prompt += f"Specifically: {user_provided_prompt}\n\n"

            prompt += (
                "Desired Format:\n"
                "TITLE: -||-\n"
                "BUCKET NAME: -||-\n"
                "FORMATTED DOCUMENTATION: -||-"
                "\n\n###\n\n"
                f"{context}\n\n"
                "TITLE: "
            )

            openai_params = eave.openai.CompletionParameters(
                prompt=prompt,
                n=1,
                frequency_penalty=0.6,
                presence_penalty=0.3,
                temperature=0.2,
            )

            openai_response = await eave.openai.summarize(openai_params)
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
        #     openai_params = eave.openai.CompletionParameters(
        #         prompt=prompt,
        #         n=1,
        #         frequency_penalty=0.6,
        #         presence_penalty=0.3,
        #         temperature=0.2,
        #     )

        #     openai_response = await eave.openai.summarize(openai_params)
        #     assert openai_response is not None
        #     return openai_response

        # document_metadata = await get_document_metadata()

        # tokens = tokencoding.encode(response)
        # truncated_content = ""
        # openai_params = eave.openai.CompletionParameters(
        #     prompt=f"Create a title for this document.\n\n###\n\n{content}\n\nTitle:\n",
        #     n=1,
        #     frequency_penalty=0,
        #     temperature=0.2,
        # )
        # title = await eave.openai.summarize(openai_params)
        # assert title is not None

        async def parse_raw_documentation() -> GeneratedDocument:
            """
            1. Parses the OpenAI response. Makes assumptions about the format of the text returned by OpenAI.
            2. Adds context to the document (eg links and source)
            """
            title, bucket_name, body = initial_generated_documentation.split("\n", maxsplit=2)
            title = re.sub("^TITLE:\\s*", "", title, flags=re.RegexFlag.IGNORECASE).strip()
            bucket_name = re.sub("^BUCKET NAME:\\s*", "", title, flags=re.RegexFlag.IGNORECASE).strip()
            body = re.sub("^FORMATTED DOCUMENTATION:\\s*", "", body, flags=re.RegexFlag.IGNORECASE).strip()

            generated_document = GeneratedDocument(title=title, content=body, bucket=bucket_name)

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
        upsert_document_response = await eave.core_api.client.upsert_document(
            title=document.title,
            content=document.content,

            source=self.message.subscription_source,
        )

        async def send_follow_up_message() -> None:
            """
            Generated a nice message and sends it back to the original Slack thread, along with a link to the new documentation.
            """
            slack_profile = await self.message.get_user_profile()
            assert slack_profile is not None

            prompt = (
                f"{PROMPT_PREFIX}\n"
                "You were recently asked to create documentation, and you've now completed that documentation. "
                f"Let {slack_profile.display_name} know about it, and remind them that you'll continously update the document as this conversation continues."
                f"{TONE_DIRECTION}"
            )

            openai_params = eave.openai.CompletionParameters(
                prompt=prompt,
                n=1,
                frequency_penalty=0,
                presence_penalty=0,
                temperature=0.2,
            )

            openai_response = await eave.openai.summarize(openai_params)
            assert openai_response is not None
            await self.respond_to_message(text=f"{openai_response}\n<{upsert_document_response.document_reference.document_url}|{document.title}>")

        await send_follow_up_message()

    async def search_documentation(self) -> None:
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
        if len(tokencoding.encode(context)) > (eave.openai.MAX_TOKENS/2):
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
            if formatted_text is None: continue

            tokens = tokencoding.encode(formatted_text)
            total_tokens += len(tokens)

            if total_tokens > (eave.openai.MAX_TOKENS/2):
                joined_messages = "\n\n".join(messages_for_prompt)
                prompt = (
                    f"{PROMPT_PREFIX}\n"
                    "Condense the following conversation. Maintain the important information."
                    "\n\n###\n\n"
                    f"{condensed_context}\n\n"
                    f"{joined_messages}\n\n"
                )
                openai_params = eave.openai.CompletionParameters(
                    prompt=prompt,
                    temperature=0.9,
                    frequency_penalty=1.0,
                    presence_penalty=1.0,
                )
                response = await eave.openai.summarize(params=openai_params)
                assert response is not None
                condensed_context = response
                total_tokens = 0
                messages_for_prompt.clear()

            messages_for_prompt.append(formatted_text)

        recent_messages = "\n\n".join(messages_for_prompt)
        return (
            f"{condensed_context}\n\n"
            f"{recent_messages}"
        )

    """
    Utility
    """

    @staticmethod
    def normalize_for_enum(value: str) -> str:
        return re.sub(pattern="\\W", repl="", string=value).upper()


    async def respond_to_message(self, text: str, caller_id: Optional[str]=None) -> None:
        assert self.message.channel is not None

        msg = f"<@{self.message.user}> {text}"
        if eave.settings.APP_SETTINGS.dev_mode:
            stack = traceback.extract_stack(limit=2)
            frame = stack[0]
            filename = os.path.basename(frame.filename)
            formatted_frame = f"{filename}:{frame.lineno}"
            msg += f" ({formatted_frame})"

        await eave.slack.client.chat_postMessage(
            channel=self.message.channel,
            text=msg,
            thread_ts=self.message.parent_ts,
        )

    async def react_to_message(self, name: str) -> None:
        assert self.message.channel is not None
        assert self.message.ts is not None
        await eave.slack.client.reactions_add(name=name, channel=self.message.channel, timestamp=self.message.ts)

    async def acknowledge_receipt(self) -> None:
        await self.react_to_message("eave")

    async def send_message_info(self) -> None:
        info = f"Subscription ID: {self.message.subscription_id}"
        await self.respond_to_message(text=info)