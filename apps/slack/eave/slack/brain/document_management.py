import json
from eave.slack.brain.subscription_management import SubscriptionManagementMixin
import eave.stdlib.analytics
import eave.stdlib.core_api.operations.documents as documents
import eave.stdlib.core_api.models.documents
from eave.stdlib.core_api.models.subscriptions import DocumentReferenceInput, SubscriptionSource
from eave.stdlib.core_api.models.subscriptions import SubscriptionInput
from eave.stdlib.exceptions import OpenAIDataError, SlackDataError
import eave.stdlib.openai_client
from eave.stdlib.logging import eaveLogger
from . import message_prompts
from . import document_metadata
from .context_building import ContextBuildingMixin
from ..config import app_config


class DocumentManagementMixin(ContextBuildingMixin, SubscriptionManagementMixin):
    async def create_documentation_and_subscribe(self) -> None:
        """
        Subscribes to the thread and creates initial documentation if not already subscribed,
        otherwise notifies the user that I'm already watching this conversation.
        """
        existing_subscription_response = await self.get_subscription()

        if existing_subscription_response is None:
            await self.send_response(
                text="On it!", eave_message_purpose="confirmation that documentation is being worked on"
            )
            subscription_response = await self.create_subscription()
            self.subscriptions.append(subscription_response.subscription)
            await self.create_documentation()
            return
        else:
            self.subscriptions.append(existing_subscription_response.subscription)
            await self.notify_existing_subscription(subscription=existing_subscription_response)
            return

    async def create_documentation(self) -> None:
        """
        A procedure to execute the following tasks:
        1. Generate documentation from the conversation
        2. Parse the generated documentation and add contextual information
        3. Send the final document to Core API (i.e. save the document to the organization's documentation destination)
        4. Send a follow-up response to the original Slack thread with a link to the documentation
        """

        api_document = await self.build_documentation()
        upsert_document_response = await self.upsert_document(document=api_document)
        await self.send_response(
            text=(
                "Here's the documentation that you asked for! I'll keep it up-to-date and accurate.\n"
                f"<{upsert_document_response.document_reference.document_url}|{api_document.title}>"
            ),
            eave_message_purpose="link to initial documentation",
        )

        self.log_event(
            event_name="eave_created_documentation",
            event_description="Eave created a new document",
            opaque_params={
                "document_platform": upsert_document_response.team.document_platform,
                "document_reference": json.loads(upsert_document_response.document_reference.json()),
                "document.title": api_document.title,
                "document.parent": api_document.parent.title if api_document.parent else None,
            },
        )

    async def build_documentation(self) -> eave.stdlib.core_api.models.documents.DocumentInput:
        conversation = await self.build_context()
        link_context = await self.build_link_context_and_subscribe()

        document_topic = await document_metadata.get_topic(conversation)
        document_hierarchy = await document_metadata.get_hierarchy(conversation)
        # project_title = await document_metadata.get_project_title(conversation)
        documentation_type = await document_metadata.get_documentation_type(conversation)
        documentation = await document_metadata.get_documentation(
            conversation=conversation,
            documentation_type=documentation_type,
            link_context=link_context,
        )
        document_resources = await self.build_resources()

        api_document = eave.stdlib.core_api.models.documents.DocumentInput(
            title=document_topic,
            content=documentation + document_resources,
        )

        current = api_document
        for category in document_hierarchy:
            p = eave.stdlib.core_api.models.documents.DocumentInput(
                title=category,
                content="",
            )
            current.parent = p
            current = p

        return api_document

    async def build_resources(self) -> str:
        all_messages = await self.message.get_conversation_messages()
        if all_messages is None:
            raise SlackDataError("all_messages")

        [await m.get_expanded_text() for m in all_messages]
        links = set([link for message in all_messages for link in message.urls])

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
        await self.send_response(
            text="On it!", eave_message_purpose="confirmation that documentation is being searched"
        )
        search_results = await self.search_documents()

        eaveLogger.debug(
            "Received search results",
            extra=self.eave_ctx.set(
                {
                    "search_results": [json.loads(d.json()) for d in search_results.documents],
                }
            ),
        )

        if len(search_results.documents) == 0:
            await self.send_response(
                text="I couldn't find any relevant documentation.",
                eave_message_purpose="notify of empty search results",
            )
            return

        link_list = [f":arrow_right: *<{result.url}|{result.title}>*" for result in search_results.documents]
        link_list_str = "\n".join(link_list)

        await self.send_response(
            text=f"Here is some relevant documentation:\n{link_list_str}",
            eave_message_purpose="provide search results",
            opaque_params={
                "search_results": [{"title": result.title, "url": result.url} for result in search_results.documents],
            },
        )

    async def update_documentation(self) -> None:
        pass
        # await self.send_response(
        #     text="I haven't yet been taught how to update existing documentation.",
        #     eave_message_purpose="unable to perform action",
        # )

    async def refine_documentation(self) -> None:
        api_document = await self.build_documentation()
        await self.upsert_document(document=api_document)

    async def archive_documentation(self) -> None:
        if len(self.subscriptions) == 0:
            await self.send_response(
                text="I haven't created any documentation from this conversation.",
                eave_message_purpose="notify can't delete documentation",
            )

        elif len(self.subscriptions) > 1:
            # TODO: Ask which one, and present options
            await self.send_response(
                text="Sorry, there are multiple documents from this conversation, and I'm not sure which one you want deleted.",
                eave_message_purpose="notify can't delete document",
            )

        else:
            document_reference_id = self.subscriptions[0].document_reference_id
            if not document_reference_id:
                await self.send_response(
                    text="I haven't created any documentation from this conversation.",
                    eave_message_purpose="notify can't delete documentation",
                )
                return

            await documents.DeleteDocument.perform(
                origin=app_config.eave_origin,
                team_id=self.eave_team.id,
                input=documents.DeleteDocument.RequestBody(
                    document_reference=DocumentReferenceInput(
                        id=document_reference_id,
                    )
                ),
            )

    async def upsert_document(self, document: eave.stdlib.core_api.models.documents.DocumentInput) -> documents.UpsertDocument.ResponseBody:
        response = await documents.UpsertDocument.perform(
            origin=app_config.eave_origin,
            team_id=self.eave_team.id,
            input=documents.UpsertDocument.RequestBody(
                subscriptions=[
                    SubscriptionInput(
                        source=SubscriptionSource(
                            platform=s.source.platform,
                            event=s.source.event,
                            id=s.source.id,
                        )
                    )
                    for s in self.subscriptions
                ],
                document=document,
            ),
        )
        return response

    async def search_documents(self) -> documents.SearchDocuments.ResponseBody:
        conversation = await self.build_context()

        prompt = eave.stdlib.openai_client.formatprompt(
            f"""
            Extract a key term or phrase from this conversation that can be used as a full-text search query to find relevant documentation.

            {message_prompts.CONVO_STRUCTURE}
            Newer messages are more relevant and should be weighted higher.
            If the newest message is asking about a specific topic, that is very important and should be your main focus.

            Conversation:
            ###
            {conversation}
            ###
            """
        )

        openai_params = eave.stdlib.openai_client.ChatCompletionParameters(
            messages=[prompt],
            n=1,
            frequency_penalty=0.9,
            presence_penalty=0.9,
            temperature=0.2,
        )

        answer: str | None = await eave.stdlib.openai_client.chat_completion(openai_params)
        if answer is None:
            raise OpenAIDataError()

        response = await documents.SearchDocuments.perform(
            origin=app_config.eave_origin,
            team_id=self.eave_team.id,
            input=documents.SearchDocuments.RequestBody(query=answer),
        )

        if len(response.documents) == 0:
            self.log_event(
                event_name="no_search_results",
                event_description="Eave returned no search results",
                opaque_params={
                    "search_query": answer,
                },
            )
        else:
            self.log_event(
                event_name="search_results",
                event_description="Eave returned search results",
                opaque_params={
                    "search_query": answer,
                    "search_results": [json.loads(d.json()) for d in response.documents],
                },
            )

        return response
