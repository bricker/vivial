import uuid
from typing import Unpack

from aiohttp.hdrs import METH_POST

from eave.stdlib.core_api.models.virtual_event import VirtualEventDetails, VirtualEventDetailsQueryInput, VirtualEventPeek
from eave.stdlib.endpoints import BaseRequestBody, BaseResponseBody

from ... import requests_util
from . import CoreApiEndpoint, CoreApiEndpointConfiguration


class ListMyVirtualEventsRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/public/me/virtual-events/list",
        method=METH_POST,
        auth_required=True,
        origin_required=True,
        is_public=True,
    )

    class RequestBody(BaseRequestBody):
        query: str | None = None

    class ResponseBody(BaseResponseBody):
        virtual_events: list[VirtualEventPeek]

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

class GetMyVirtualEventDetailsRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/public/me/virtual-events/query",
        method=METH_POST,
        auth_required=True,
        origin_required=True,
        is_public=True,
    )

    class RequestBody(BaseRequestBody):
        virtual_event: VirtualEventDetailsQueryInput

    class ResponseBody(BaseResponseBody):
        virtual_event: VirtualEventDetails

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
