from typing import Optional
import uuid
from eave.stdlib.core_api.models.subscriptions import DocumentReference
from eave.stdlib.core_api.models.subscriptions import Subscription
from eave.stdlib.core_api.models.subscriptions import DocumentReferenceInput
from eave.stdlib.core_api.models.subscriptions import SubscriptionInput
from . import BaseRequestBody, BaseResponseBody, EndpointConfiguration

from eave.stdlib.eave_origins import EaveOrigin
from . import Endpoint
from ..models import team
from ... import requests
from ... import exceptions


class GetSubscriptionRequest(Endpoint):
    config = EndpointConfiguration(
        path="/subscriptions/query",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        subscription: SubscriptionInput

    class ResponseBody(BaseResponseBody):
        team: team.Team
        subscription: Optional[Subscription]
        document_reference: Optional[DocumentReference] = None

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


class CreateSubscriptionRequest(Endpoint):
    config = EndpointConfiguration(
        path="/subscriptions/create",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        subscription: SubscriptionInput
        document_reference: Optional[DocumentReferenceInput] = None

    class ResponseBody(BaseResponseBody):
        team: team.Team
        subscription: Subscription
        document_reference: Optional[DocumentReference] = None

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


class DeleteSubscriptionRequest(Endpoint):
    config = EndpointConfiguration(
        path="/subscriptions/delete",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        subscription: SubscriptionInput

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
