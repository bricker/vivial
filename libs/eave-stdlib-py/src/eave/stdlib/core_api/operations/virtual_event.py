from typing import Optional, Unpack
import uuid
from eave.stdlib.core_api.models.virtual_event import VirtualEvent, VirtualEventQueryInput
from . import BaseRequestBody, BaseResponseBody, CoreApiEndpoint, CoreApiEndpointConfiguration

from ... import requests


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
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            access_token=access_token,
            account_id=account_id,
            team_id=team_id,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body
