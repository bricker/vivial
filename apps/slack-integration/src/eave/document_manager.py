import asyncio
import logging
import re
from dataclasses import dataclass
from uuid import uuid4

import eave.eave_core as eave_core
import eave.openai_proxy as openai_proxy
import eave.prompts as prompts
import eave.slack_app as slack
from eave.slack_models import SlackMessage


@dataclass
class GeneratedDocument:
    title: str
    content: str


class DocumentManager:
    def __init__(self, message: SlackMessage, subscription: eave_core.Subscription) -> None:
        self.message = message
        self.subscription = subscription

    async def process_message(self) -> eave_core.EaveCoreClient.UpsertDocumentResponse | None:
        eave_core_client = eave_core.EaveCoreClient()
        new_document = await self.generate_document()

        if new_document is None:
            logging.warning("couldnt generate document")
            return None

        response = await eave_core_client.upsert_document(
            title=new_document.title,
            content=new_document.content,
            source=self.subscription.source,
        )

        if self.message.channel is not None:
            await slack.client.chat_postMessage(
                channel=self.message.channel,
                thread_ts=self.message.parent_ts,
                text=f":thumbsup: <{response.document_reference.document_url}|{new_document.title}>",
            )

        return response

    async def generate_document(self) -> GeneratedDocument | None:
        formatted_conversation = await self.message.get_formatted_conversation()

        if formatted_conversation is None:
            logging.warning("formatted conversation could not be generated.")
            return None

        content, permalink = await asyncio.gather(
            openai_proxy.summarize(prompt=prompts.build_prompt(formatted_conversation)),
            self.message.get_parent_permalink(),
        )

        if content is None:
            logging.error("No content was generated")
            return None

        if permalink is not None:
            doc_source = permalink.permalink
        else:
            doc_source = "Unknown Slack message"

        content += f"\n\n<{doc_source}|Source>"
        parsed_content = self.parse_openai_response(content)
        return parsed_content

    def parse_openai_response(self, content: str) -> GeneratedDocument:
        match = re.match("^title: (.+)$", content, flags=re.IGNORECASE)
        title = match.groups()[0] if match is not None else str(uuid4())

        match = re.match("^category: (.+)$", content, flags=re.IGNORECASE)
        category = match.groups()[0] if match is not None else None

        match = re.match("^topics: (.+)$", content, flags=re.IGNORECASE)
        topics = match.groups()[0] if match is not None else None

        match = re.match("^tags: (.+)$", content, flags=re.IGNORECASE)
        tags = match.groups()[0] if match is not None else None

        match = re.match("^summary: (.+)$", content, flags=re.IGNORECASE)
        summary = match.groups()[0] if match is not None else None

        match = re.match("^outcome: (.+)$", content, flags=re.IGNORECASE)
        outcome = match.groups()[0] if match is not None else None

        return GeneratedDocument(title=title, content=content)
