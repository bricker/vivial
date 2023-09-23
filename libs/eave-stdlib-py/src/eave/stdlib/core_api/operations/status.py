import aiohttp

from . import BaseResponseBody, CoreApiEndpoint, CoreApiEndpointConfiguration

from . import Endpoint


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

            response_json = await response.json()

        return cls.ResponseBody(**response_json, _raw_response=response)
