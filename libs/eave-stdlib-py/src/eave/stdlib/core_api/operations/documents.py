from typing import Optional, TypeAlias
import uuid

from eave.stdlib.core_api.models.documents import DocumentSearchResult
from eave.stdlib.core_api.models.documents import DocumentInput
from . import BaseRequestBody, BaseResponseBody, EndpointConfiguration

from ..models.subscriptions import DocumentReference, DocumentReferenceInput, Subscription
from ..models.subscriptions import SubscriptionInput

from ...eave_origins import EaveOrigin
from . import Endpoint
from ..models import team
from ... import requests


class UpsertDocument(Endpoint):
    config = EndpointConfiguration(
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
        origin: EaveOrigin,
        input: RequestBody,
        team_id: uuid.UUID,
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            origin=origin,
            input=input,
            team_id=team_id,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)

class SearchDocuments(Endpoint):
    config = EndpointConfiguration(
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
        cls,
        origin: EaveOrigin,
        input: RequestBody,
        team_id: uuid.UUID,
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            origin=origin,
            input=input,
            team_id=team_id,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)

class DeleteDocument(Endpoint):
    config = EndpointConfiguration(
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
        origin: EaveOrigin,
        input: RequestBody,
        team_id: uuid.UUID,
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            origin=origin,
            input=input,
            team_id=team_id,
        )

        return cls.ResponseBody(_raw_response=response)
