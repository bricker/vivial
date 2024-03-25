import uuid
from typing import Optional, Unpack

from eave.stdlib.core_api.models.virtual_event import VirtualEvent, VirtualEventQueryInput
from eave.stdlib.endpoints import BaseRequestBody, BaseResponseBody

from . import CoreApiEndpoint, CoreApiEndpointConfiguration
from ... import requests_util


class GetVirtualEventsRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/virtual-events/query",
    )

    class RequestBody(BaseRequestBody):
        virtual_events: Optional[VirtualEventQueryInput] = None

    class ResponseBody(BaseResponseBody):
        virtual_events: list[VirtualEvent]

    @classmethod
    async def perform(
        cls,
        access_token: str,
        team_id: uuid.UUID | str,
        account_id: uuid.UUID | str,
        input: RequestBody,
        **kwargs: Unpack[requests_util.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests_util.make_request(
            config=cls.config,
            input=input,
            access_token=access_token,
            account_id=account_id,
            team_id=team_id,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body
