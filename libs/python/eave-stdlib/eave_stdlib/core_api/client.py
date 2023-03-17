from typing import Optional
import urllib.parse
import aiohttp
from . import operations

class EaveCoreClient:
    api_base_url: str

    def __init__(self, api_base_url: str) -> None:
        self.api_base_url = api_base_url

    async def create_access_request(
        self, input: operations.CreateAccessRequest.RequestBody,
    ) -> None:
        """
        POST /access_request
        """
        async with aiohttp.ClientSession() as session:
            response = await session.request(
                "POST",
                self.makeurl("/access_request"),
                headers={},
                json=input.json(),
            )

        return None

    async def upsert_document(
        self, input: operations.UpsertDocument.RequestBody,
    ) -> operations.UpsertDocument.ResponseBody:
        """
        POST /documents/upsert
        """
        async with aiohttp.ClientSession() as session:
            response = await session.request(
                "POST",
                self.makeurl("/documents/upsert"),
                headers={},
                json=input.json(),
            )

        response_json = await response.json()
        response = operations.UpsertDocument.ResponseBody(**response_json)
        return response

    async def create_subscription(
        self, input: operations.CreateSubscription.RequestBody,
    ) -> operations.CreateSubscription.ResponseBody:
        """
        POST /subscriptions/create
        """
        async with aiohttp.ClientSession() as session:
            response = await session.request(
                "POST",
                self.makeurl("/subscriptions/create"),
                headers={},
                json=input.json(),
            )

        response_json = await response.json()
        return operations.CreateSubscription.ResponseBody(**response_json)

    async def get_subscription(self, input: operations.GetSubscription.RequestBody) -> Optional[operations.GetSubscription.ResponseBody]:
        """
        POST /subscriptions/query
        """
        async with aiohttp.ClientSession() as session:
            response = await session.request(
                "POST",
                self.makeurl("/subscriptions/query"),
                headers={},
                json=input.json(),
            )

        if response.status >= 300:
            return None

        response_json = await response.json()
        return operations.GetSubscription.ResponseBody(**response_json)

    def makeurl(self, path: str) -> str:
        return urllib.parse.urljoin(self.api_base_url, path)
