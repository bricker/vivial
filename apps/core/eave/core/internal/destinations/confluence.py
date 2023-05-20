import typing
from functools import cached_property
from typing import Optional, cast

import atlassian
import eave.stdlib
import eave.stdlib.atlassian
from eave.stdlib.core_api.models import DocumentSearchResult
import eave.stdlib.core_api.operations as eave_ops
from eave.stdlib.exceptions import ConfluenceDataError, OpenAIDataError
from eave.stdlib.logging import eaveLogger
import eave.stdlib.openai_client
from eave.stdlib.util import unwrap

from ..oauth import atlassian as atlassian_oauth
from . import abstract


class ConfluenceDestination(abstract.DocumentDestination):
    oauth_session: atlassian_oauth.AtlassianOAuthSession
    atlassian_cloud_id: str
    space: Optional[str]

    def __init__(
        self, oauth_session: atlassian_oauth.AtlassianOAuthSession, atlassian_cloud_id: str, space: Optional[str]
    ) -> None:
        self.oauth_session = oauth_session
        self.atlassian_cloud_id = atlassian_cloud_id
        self.space = space

    def get_available_spaces(self) -> typing.List[eave.stdlib.atlassian.ConfluenceSpace]:
        """
        https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-space/#api-wiki-rest-api-space-get
        """
        response = self._confluence_client.get_all_spaces(space_status="current", space_type="global")
        response_json = cast(eave.stdlib.typing.JsonObject, response)
        return [eave.stdlib.atlassian.ConfluenceSpace(s) for s in response_json["results"]]

    async def search_documents(self, query: str) -> list[DocumentSearchResult]:
        try:
            cql = f"space={self.space} AND text ~ {query}"
            eaveLogger.debug(f"Confluence CQL query: {cql}")
            response = self._confluence_client.cql(cql=cql)

            if response is None:
                raise ConfluenceDataError("cql results")

            json = cast(eave.stdlib.typing.JsonObject, response)
            if (results := json.get("results")) is None:
                raise ConfluenceDataError("cql results")
        except Exception:
            eaveLogger.exception("Error while fetching search results from Confluence")
            return []

        pages = [
            eave.stdlib.atlassian.ConfluencePage(content) for result in results if (content := result.get("content"))
        ]
        base_url = self.oauth_session.confluence_context.base_url
        return [DocumentSearchResult(title=(page.title or ""), url=page.canonical_url(base_url)) for page in pages]

    async def create_document(self, input: eave_ops.DocumentInput) -> abstract.DocumentMetadata:
        confluence_page = await self._get_or_create_confluence_page(document=input)
        base_url = self.oauth_session.confluence_context.base_url
        return abstract.DocumentMetadata(
            id=unwrap(confluence_page.id, ""),
            url=confluence_page.canonical_url(base_url),
        )

    async def update_document(
        self,
        input: eave_ops.DocumentInput,
        document_id: str,
    ) -> abstract.DocumentMetadata:
        """
        Update an existing Confluence document with the new body.
        Notably, the title and parent are not changed.
        """
        existing_page = await self._get_confluence_page_by_id(document_id=document_id)
        if existing_page is None:
            # TODO: This page was probably deleted. Remove it from our database?
            raise NotImplementedError()

        # TODO: Use a different body format? Currently it will probably return the "storage" format,
        # which is XML (HTML), and probably not great for an OpenAI prompt.
        if existing_page.body is not None and existing_page.body.content is not None:
            # TODO: Token counting
            prompt = (
                "Merge the following two documents."
                "\n\n"
                "First Document:\n"
                "=========================\n"
                f"{existing_page.body.content}\n"
                "=========================\n\n"
                "Second Document:\n"
                "=========================\n"
                f"{input.content}\n"
                "=========================\n"
            )
            openai_params = eave.stdlib.openai_client.ChatCompletionParameters(
                temperature=0.2,
                messages=[prompt],
            )
            resolved_document_body = await eave.stdlib.openai_client.chat_completion(params=openai_params)

            if resolved_document_body is None:
                raise OpenAIDataError()

        else:
            resolved_document_body = input.content

        # TODO: Hack
        content = resolved_document_body.replace("&", "&amp;")
        response = self._confluence_client.update_page(
            page_id=document_id,
            title=existing_page.title,
            body=content,
        )

        if response is None:
            raise ConfluenceDataError("confluence update_page response")

        json = cast(eave.stdlib.typing.JsonObject, response)
        page = eave.stdlib.atlassian.ConfluencePage(json)
        base_url = self.oauth_session.confluence_context.base_url
        return abstract.DocumentMetadata(
            id=page.id or "",
            url=page.canonical_url(base_url),
        )

    @cached_property
    def _confluence_client(self) -> atlassian.Confluence:
        """
        Atlassian Python API Docs: https://atlassian-python-api.readthedocs.io/
        """
        return atlassian.Confluence(
            url=self.oauth_session.api_base_url,
            session=self.oauth_session,
        )

    async def _get_or_create_confluence_page(
        self, document: eave_ops.DocumentInput
    ) -> eave.stdlib.atlassian.ConfluencePage:
        existing_page = await self._get_confluence_page_by_title(document=document)
        if existing_page:
            return existing_page

        parent_page = None
        if document.parent is not None:
            parent_page = await self._get_or_create_confluence_page(document=document.parent)

        # TODO: Hack
        content = document.content.replace("&", "&amp;")
        response = self._confluence_client.create_page(
            space=self.space,
            title=document.title,
            body=content,
            parent_id=parent_page.id if parent_page is not None else None,
        )

        if response is None:
            raise ConfluenceDataError("confluence create_page response")

        json = cast(eave.stdlib.typing.JsonObject, response)
        page = eave.stdlib.atlassian.ConfluencePage(json)
        return page

    async def _get_confluence_page_by_id(
        self,
        document_id: str,
    ) -> eave.stdlib.atlassian.ConfluencePage | None:
        response = self._confluence_client.get_page_by_id(
            page_id=document_id,
            expand=["history"],
        )
        if response is None:
            return None

        json = cast(eave.stdlib.typing.JsonObject, response)
        page = eave.stdlib.atlassian.ConfluencePage(json)
        return page

    async def _get_confluence_page_by_title(
        self, document: eave_ops.DocumentInput
    ) -> eave.stdlib.atlassian.ConfluencePage | None:
        response = self._confluence_client.get_page_by_title(
            space=self.space,
            title=document.title,
        )
        if response is None:
            return None

        json = cast(eave.stdlib.typing.JsonObject, response)
        page = eave.stdlib.atlassian.ConfluencePage(json)
        return page
