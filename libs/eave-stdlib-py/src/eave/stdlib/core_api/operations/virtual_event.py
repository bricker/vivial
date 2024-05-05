import uuid
from typing import Unpack

from eave.stdlib.core_api.models.virtual_event import VirtualEvent, VirtualEventQueryInput
from eave.stdlib.endpoints import BaseRequestBody, BaseResponseBody

from ... import requests_util
from . import CoreApiEndpoint, CoreApiEndpointConfiguration


class GetMyVirtualEventsRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/_/me/virtual-events/query",
        auth_required=True,
        origin_required=True,
        is_public=False,
    )

    class RequestBody(BaseRequestBody):
        virtual_events: VirtualEventQueryInput | None = None

    class ResponseBody(BaseResponseBody):
        virtual_events: list[VirtualEvent]

    @classmethod
    async def perform(
        cls,
        *,
        account_id: uuid.UUID | str,
        access_token: str,
        input: RequestBody,
        **kwargs: Unpack[requests_util.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests_util.make_request(
            config=cls.config,
            input=input,
            access_token=access_token,
            account_id=account_id,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body
