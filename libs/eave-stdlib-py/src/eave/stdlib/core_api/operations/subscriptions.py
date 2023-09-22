from typing import Optional, Unpack
import uuid
from eave.stdlib.core_api.models.subscriptions import DocumentReference
from eave.stdlib.core_api.models.subscriptions import Subscription
from eave.stdlib.core_api.models.subscriptions import DocumentReferenceInput
from eave.stdlib.core_api.models.subscriptions import SubscriptionInput
from . import BaseRequestBody, BaseResponseBody, CoreApiEndpoint, CoreApiEndpointConfiguration

from . import Endpoint
from ..models import team
from ... import requests


class GetSubscriptionRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
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


class CreateSubscriptionRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
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


class DeleteSubscriptionRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
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
