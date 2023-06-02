import aiohttp

from . import BaseResponseBody

from . import Endpoint
from ... import requests


class Status(Endpoint):
    class ResponseBody(BaseResponseBody):
        service: str
        version: str
        status: str

    @classmethod
    async def perform(cls) -> ResponseBody:
        async with aiohttp.ClientSession() as session:
            response = await session.request(
                "GET",
                requests.makeurl("/status"),
            )

            response_json = await response.json()

        return cls.ResponseBody(**response_json, _raw_response=response)
