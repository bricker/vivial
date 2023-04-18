import asyncio
import json
import random
from typing import Optional
from uuid import UUID

import eave.pubsub_schemas.generated.eave_user_action_pb2 as eave_user_action
import eave.stdlib.analytics
import eave.stdlib.core_api.client as eave_core_api_client
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.operations as eave_ops
import eave.stdlib.openai_client as eave_openai
import tiktoken
from eave.stdlib import logger

from . import document_metadata, message_prompts, slack_models

tokencoding = tiktoken.get_encoding("gpt2")


class Brain:
    message: slack_models.SlackMessage
    user_profile: Optional[slack_models.SlackProfile]
    expanded_text: str
    message_context: str
    team_id: UUID

    def __init__(self, message: slack_models.SlackMessage) -> None:
        self.message = message
        # FIXME: Hardcoded ID
        self.team_id = UUID("3345217c-fb27-4422-a3fc-c404b49aff8c")
        # self.team = await eave_core_api_client.get_team(slack_org_id: xxx)

    async def process_message(self) -> None:
        logger.debug("Brain.process_message")

        await self.load_data()

        i_am_mentioned = await self.message.check_eave_is_mentioned()
        if i_am_mentioned is True:
            """
            Eave is mentioned in this message.
            1. Acknowledge receipt of the message.
            1. If she's being asked for thread information, handle that and stop processing.
            1. Otherwise, send a preliminary response and continue processing.
            """
            await self.acknowledge_receipt()

            action = eave_user_action.EaveUserAction(
                action=eave_user_action.EaveUserAction.Action(
                    platform=eave_models.SubscriptionSourcePlatform.slack,
                    name="eave_mention",
                    description="Eave was mentioned in Slack",
                    eave_user_id="xxxx",
                    opaque_params=json.dumps({}),
                    user_ts=int(float(self.message.ts)),
                ),
                message_source=__name__,
            )
            eave.stdlib.analytics.log_user_action(action=action)

            message_action = await message_prompts.message_action(context=self.message_context)

        else:
            """
            Eave is not mentioned in this message.
            1. Lookup an existing subscription for this source.
            1. If she is not subscribed, then ignore the message and stop processing.
            1. Otherwise, continue processing.
            """
            subscription_response = await self.get_subscription()
            if subscription_response is None:
                logger.debug("Eave is not subscribed to this thread; ignoring.")
                return

            message_action = message_prompts.MessageAction.REFINE_DOCUMENTATION

        await self.handle_action(message_action=message_action)

    async def process_shortcut_event(self) -> None:
        logger.debug("Brain.shortcut_event")
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

    async def handle_action(self, message_action: message_prompts.MessageAction) -> None:
        match message_action:
            case message_prompts.MessageAction.CREATE_DOCUMENTATION | message_prompts.MessageAction.WATCH:
                await self.create_documentation_and_subscribe()
                return

            case message_prompts.MessageAction.UNWATCH:
                await self.unwatch_conversation()
                return

            case message_prompts.MessageAction.SEARCH_DOCUMENTATION:
                await self.message.send_response(text="One moment while I look...")
                await self.search_documentation()
                return

            case message_prompts.MessageAction.UPDATE_DOCUMENTATION:
                await self.message.send_response(text="On it!")
                await self.update_documentation()
                return

            case message_prompts.MessageAction.REFINE_DOCUMENTATION:
                await self.refine_documentation()
                return

            case message_prompts.MessageAction.DELETE_DOCUMENTATION:
                # TODO: Unsubscribe from conversation
                await self.message.send_response(text="On it!")
                await self.archive_documentation()
                return

            case message_prompts.MessageAction.NONE:
                return

            case _:
                await self.handle_unknown_request()
                return

    async def create_documentation_and_subscribe(self) -> None:
        """
        Subscribes to the thread and creates initial documentation if not already subscribed,
        otherwise notifies the user that I'm already watching this conversation.
        """
        logger.debug("Brain.process_watch_request")
        existing_subscription = await self.get_subscription()

        if existing_subscription is None:
            message_prefix = random.choice(
                (
                    "Acknowledged!",
                    "On it!",
                    "Got it!",
                    "Got it.",
                )
            )
            await self.message.send_response(
                text=(
                    f"{message_prefix} I'll get started on the documentation right now and send an update when it's ready."
                )
            )
            await self.create_subscription()
            await self.create_documentation()
            return
        else:
            await self.notify_existing_subscription(subscription=existing_subscription)
            return

    async def handle_unknown_request(self) -> None:
        """
        Processes a request that wasn't recognized.
        Basically lets the user know that I wasn't able to process the message, and reminds them if I'm already documenting this conversation.
        """
        logger.debug("Brain.process_unknown_request")
        subscription = await self.get_subscription()

        # TODO: Create a Jira ticket (or similar) when Eave doesn't know how to handle a message.

        if subscription is None:
            await self.message.send_response(
                text=(
                    "Hey! I haven't been trained on how to respond to your message. I've let my development team know about it. "
                    f"Do you want me to watch and document this conversation? (This feature is not yet implemented) "
                    "If you needed something else, try phrasing it differently."
                )
            )

            # TODO: handle the response to this, eg if the user says "Yes please" or "No thanks"

        elif subscription.document_reference is not None:
            await self.message.send_response(
                text=(
                    "Hey! I haven't been trained on how to respond to your message. I've let my development team know about it. "
                    f"As a reminder, I'm watching this conversation and documenting the information <{subscription.document_reference.document_url}|here>. "
                    "If you needed something else, try phrasing it differently."
                )
            )

        else:
            await self.message.send_response(
                text=(
                    "Hey! I haven't been trained on how to respond to your message. I've let my development team know about it. "
                    f"I'm currently working on the documentation for this conversation, and I'll send an update when it's ready. "
                    "If you needed something else, try phrasing it differently."
                )
            )

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
        logger.debug("Brain.create_documentation")

        api_document = await self.build_documentation()
        upsert_document_response = await self.upsert_document(document=api_document)

        await self.message.send_response(
            text=(
                "Here's the documentation that you asked for! I'll keep it up-to-date and accurate.\n"
                f"<{upsert_document_response.document_reference.document_url}|{api_document.title}>"
            )
        )

    async def build_documentation(self) -> eave_ops.DocumentInput:
        logger.debug("Brain.build_documentation")
        conversation = await self.build_context()

        document_topic = await document_metadata.get_topic(conversation)
        logger.info(f"document_topic: {document_topic}")
        document_hierarchy = await document_metadata.get_hierarchy(conversation)
        logger.info(f"document_hierarchy: {document_hierarchy}")
        project_title = await document_metadata.get_project_title(conversation)
        logger.info(f"project_title: {project_title}")
        documentation_type = await document_metadata.get_documentation_type(conversation)
        logger.info(f"documentation_type: {documentation_type}")
        documentation = await document_metadata.get_documentation(
            conversation=conversation, documentation_type=documentation_type
        )
        logger.info(f"documentation:\n{documentation}")
        document_resources = await self.build_resources()
        logger.info(f"document_resources: {document_resources}")

        api_document = eave_ops.DocumentInput(
            title=document_topic,
            content=documentation + document_resources,
        )

        current = api_document
        for category in document_hierarchy:
            p = eave_ops.DocumentInput(
                title=category,
                content="",
            )
            current.parent = p
            current = p

        return api_document

    async def build_resources(self) -> str:
        all_messages = await self.message.get_conversation_messages()
        assert all_messages is not None

        [await m.get_expanded_text() for m in all_messages]
        # TODO: Remove duplicate URLs
        links = [link for message in all_messages for link in message.urls]

        resources_doc = ""

        if len(links) > 0:
            resources_doc += "<h3>Resources</h3>" "<ol>"
            for link in links:
                parts = link.split("|")
                if len(parts) > 1:
                    name = parts[1]
                    url = parts[0]
                else:
                    name = parts[0]
                    url = parts[0]

                resources_doc += "<li>" f'<a href="{url}">{name}</a>' "</li>"

            resources_doc += "</ol>"

        resources_doc += "<h3>Source</h3>"

        permalink = await self.message.get_parent_permalink()
        if permalink is not None:
            doc_source = str(permalink.permalink)
            resources_doc += f'<a href="{doc_source}">Slack</a>'
        else:
            resources_doc += f"Slack message: {self.message.subscription_id}"

        return resources_doc

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
        # await self.message.send_response(blocks=blocks)

        await self.message.send_response(text="I haven't yet been taught how to search existing documentation.")

    async def update_documentation(self) -> None:
        await self.message.send_response(text="I haven't yet been taught how to update existing documentation.")

    async def refine_documentation(self) -> None:
        api_document = await self.build_documentation()
        await self.upsert_document(document=api_document)

    async def archive_documentation(self) -> None:
        await self.message.send_response(text="I haven't yet been taught how to archive existing documentation.")

    async def unwatch_conversation(self) -> None:
        await eave_core_api_client.delete_subscription(
            team_id=self.team_id,
            input=eave_ops.DeleteSubscription.RequestBody(
                subscription=eave_ops.SubscriptionInput(source=self.message.subscription_source),
            ),
        )

        await self.message.send_response(text="You got it! I'll stop watching this conversation.")

    """
    Context Building
    """

    async def build_context(self) -> str:
        context = await self.build_concatenated_context()
        if len(tokencoding.encode(context)) > (eave_openai.MAX_TOKENS[eave_openai.OpenAIModel.GPT4] / 2):
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

            if total_tokens > (eave_openai.MAX_TOKENS[eave_openai.OpenAIModel.GPT4] / 2):
                joined_messages = "\n\n".join(messages_for_prompt)
                prompt = eave_openai.formatprompt(
                    f"""
                    Condense the following conversation. Maintain the important information.

                    ###

                    {condensed_context}

                    {joined_messages}

                    ###
                """
                )
                openai_params = eave_openai.ChatCompletionParameters(
                    model=eave_openai.OpenAIModel.GPT4,
                    messages=[prompt],
                    temperature=0.9,
                    frequency_penalty=1.0,
                    presence_penalty=1.0,
                )
                response = await eave_openai.chat_completion(params=openai_params)
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

    async def acknowledge_receipt(self) -> None:
        # TODO: Check if an "eave" emoji exists in the workspace. If not, use eg "thumbsup"
        await self.message.add_reaction("eave")

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

    async def upsert_document(self, document: eave_ops.DocumentInput) -> eave_ops.UpsertDocument.ResponseBody:
        response = await eave_core_api_client.upsert_document(
            team_id=self.team_id,
            input=eave_ops.UpsertDocument.RequestBody(
                subscription=eave_ops.SubscriptionInput(source=self.message.subscription_source),
                document=document,
            ),
        )
        return response

    async def notify_existing_subscription(self, subscription: eave_ops.GetSubscription.ResponseBody) -> None:
        if subscription.document_reference is not None:
            await self.message.send_response(
                text=(
                    f"Hey! I'm already watching this conversation and documenting the information <{subscription.document_reference.document_url}|here>. "
                    "Let me know if you need anything else!"
                )
            )
            return

        else:
            await self.message.send_response(
                text=(
                    f"Hey! I'm currently working on the documentation for this conversation. I'll send an update when it's ready."
                )
            )
            return

    async def load_data(self) -> None:
        user_profile = await self.message.get_user_profile()
        self.user_profile = user_profile

        expanded_text = await self.message.get_expanded_text()
        assert expanded_text is not None
        self.expanded_text = expanded_text

        # TODO finish impl
        await self.message.resolve_urls()
        # TODO: make flex enough to support non-code links. I can imagine looking inside jira tix as well
        source_links: list[str] = list(filter(lambda x: is_a_supported_link(x), self.message.urls))
        # only do deeper api requests if there are any code links to begin with
        if source_links:
            # TODO: fetch from db what soureces are connected. coreapi request?
            available_sources = await eave_core_api_client.get_code_sources()
            # TODO: take note of enterprise paths; cant rely on public domain name pattern
            accessible_source_links: list[str] = list(filter(lambda x: is_prefix_of(available_sources, x), source_links))

            # TODO contact source code api of the linked source hubs. coreapi request??
            # TODO: the gh link could hypothetically be one that our oauth token doesn't provide access to. should handle failures to fetch
            source_text = await eave_core_api_client.get_source_code(accessible_source_links)
            assert source_text is not None
            self.source_text = source_text

        await self.build_message_context()

    async def build_message_context(self) -> None:
        context: list[str] = []

        if self.user_profile is not None:
            caller_name = self.user_profile.real_name_normalized
            caller_job_title = self.user_profile.title

            context.append(f"{caller_name} sent you a message.")
            if caller_job_title: # might be empty string
                context.append(f'{caller_name}\'s job title is "{caller_job_title}".')

        # f"The question was asked in a Slack channel called \"\". "
        # f"The description of that channel is: \"\" "

        compiled_context = "\n".join(context)

        message_context = eave_openai.formatprompt(
            compiled_context,
            f"""
            Message:
            ###
            {self.expanded_text}
            ###
        """,
        )

        self.message_context = message_context
