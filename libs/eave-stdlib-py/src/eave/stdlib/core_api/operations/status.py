import aiohttp
from eave.stdlib.endpoints import BaseResponseBody

from . import CoreApiEndpoint, CoreApiEndpointConfiguration


class Status(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/status",
        method="GET",
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
                cls.config.method,
                cls.config.url,
            )

            # This must remain inside of the ClientSession context, so that the body stream is still open when it is read.
            body = await cls.make_response(response, cls.ResponseBody)

        return body
