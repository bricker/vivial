from typing import Unpack
import uuid

from eave.stdlib.core_api.models.documents import DocumentSearchResult
from eave.stdlib.core_api.models.documents import DocumentInput
from . import BaseRequestBody, BaseResponseBody, CoreApiEndpoint, CoreApiEndpointConfiguration

from ..models.subscriptions import DocumentReference, DocumentReferenceInput, Subscription
from ..models.subscriptions import SubscriptionInput

from ..models import team
from ... import requests


class UpsertDocument(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/documents/upsert",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        document: DocumentInput
        subscriptions: list[SubscriptionInput]

    class ResponseBody(BaseResponseBody):
        team: team.Team
        subscriptions: list[Subscription]
        document_reference: DocumentReference

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        team_id: uuid.UUID,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class SearchDocuments(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/documents/search",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        query: str

    class ResponseBody(BaseResponseBody):
        team: team.Team
        documents: list[DocumentSearchResult]

    @classmethod
    async def perform(
        cls, input: RequestBody, team_id: uuid.UUID, **kwargs: Unpack[requests.CommonRequestArgs]
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class DeleteDocument(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/documents/delete",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        document_reference: DocumentReferenceInput

    class ResponseBody(BaseResponseBody):
        pass

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        team_id: uuid.UUID,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        return cls.ResponseBody(_raw_response=response)
