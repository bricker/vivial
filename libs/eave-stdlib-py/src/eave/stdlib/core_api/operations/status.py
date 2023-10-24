import aiohttp

from eave.stdlib.api_types import BaseResponseBody
from eave.stdlib.requests import make_response

from . import CoreApiEndpoint, CoreApiEndpointConfiguration


class Status(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/status",
        auth_required=False,
        team_id_required=False,
        signature_required=False,
        origin_required=False,
    )

    class ResponseBody(BaseResponseBody):
        service: str
        version: str
        status: str

    @classmethod
    async def perform(cls) -> ResponseBody:
        async with aiohttp.ClientSession() as session:
            response = await session.request(
                "GET",
                cls.config.url,
            )

            # This must remain inside of the ClientSession context, so that the body stream is still open when it is read.
            body = await make_response(response=response, response_type=cls.ResponseBody)

        return body
