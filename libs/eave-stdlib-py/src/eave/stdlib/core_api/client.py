from http import HTTPStatus
import urllib.parse
from typing import Optional
from uuid import UUID

import aiohttp
import pydantic

from .. import logger, signing
from ..config import shared_config
from . import operations
from . import headers as eave_headers
from . import _ORIGIN

class EaveCoreApiClient:
    _access_token: str
    _refresh_token: str

    async def status(self) -> operations.Status.ResponseBody:
        async with aiohttp.ClientSession() as session:
            response = await session.request(
                "GET",
                self._makeurl("/status"),
            )

        response_json = await response.json()
        return operations.Status.ResponseBody(**response_json)


    async def create_access_request(
        self,
        input: operations.CreateAccessRequest.RequestBody,
    ) -> None:
        """
        POST /access_request
        """
        await self._make_request(
            path="/access_request",
            input=input,
        )


    async def upsert_document(
        self,
        team_id: UUID,
        input: operations.UpsertDocument.RequestBody,
    ) -> operations.UpsertDocument.ResponseBody:
        """
        POST /documents/upsert
        """
        response = await self._make_request(
            path="/documents/upsert",
            input=input,
            team_id=str(team_id),
        )

        response_json = await response.json()
        return operations.UpsertDocument.ResponseBody(**response_json)


    async def create_subscription(
        self,
        team_id: UUID,
        input: operations.CreateSubscription.RequestBody,
    ) -> operations.CreateSubscription.ResponseBody:
        """
        POST /subscriptions/create
        """
        response = await self._make_request(
            path="/subscriptions/create",
            input=input,
            team_id=str(team_id),
        )

        response_json = await response.json()
        return operations.CreateSubscription.ResponseBody(**response_json)


    async def delete_subscription(
        self,
        team_id: UUID,
        input: operations.DeleteSubscription.RequestBody,
    ) -> None:
        """
        POST /subscriptions/delete
        """
        await self._make_request(
            path="/subscriptions/delete",
            input=input,
            team_id=str(team_id),
        )


    async def get_subscription(
        self,
        team_id: UUID, input: operations.GetSubscription.RequestBody
    ) -> Optional[operations.GetSubscription.ResponseBody]:
        """
        POST /subscriptions/query
        """
        response = await self._make_request(
            path="/subscriptions/query",
            input=input,
            team_id=str(team_id),
        )

        if response.status >= 300:
            return None

        response_json = await response.json()
        return operations.GetSubscription.ResponseBody(**response_json)


    async def get_slack_installation(
        self,
        input: operations.GetSlackInstallation.RequestBody,
    ) -> Optional[operations.GetSlackInstallation.ResponseBody]:
        """
        POST /installations/slack/query
        """
        # fetch slack bot details
        response = await self._make_request(
            path="/installations/slack/query",
            input=input,
        )

        if response.status >= 300:
            return None

        response_json = await response.json()
        return operations.GetSlackInstallation.ResponseBody(**response_json)

    async def request_access_token(
        self,
        input: operations.RequestAccessToken.RequestBody,
    ) -> None:
        """
        POST /auth/token/request
        """
        response = await self._make_request(
            path="/auth/token/request",
            input=input,
        )

        response_json = await response.json()
        response_obj = operations.RequestAccessToken.ResponseBody(**response_json)
        self._access_token = response_obj.access_token
        self._refresh_token = response_obj.refresh_token

    async def refresh_access_token(
        self,
        input: operations.RefreshAccessToken.RequestBody,
    ) -> None:
        """
        POST /auth/token/refresh
        """
        response = await self._make_request(
            path="/auth/token/refresh",
            input=input,
            use_auth=True,
        )

        response_json = await response.json()
        response_obj = operations.RefreshAccessToken.ResponseBody(**response_json)
        self._access_token = response_obj.access_token
        self._refresh_token = response_obj.refresh_token

    async def _make_request(self, path: str, input: pydantic.BaseModel, use_auth: bool = False, team_id: Optional[str] = None) -> aiohttp.ClientResponse:
        method = "POST"
        url = self._makeurl(path)
        payload = input.json()

        headers = {
            "content-type": "application/json",
            eave_headers.EAVE_ORIGIN_HEADER: _ORIGIN.value,
        }

        if use_auth:
            headers[eave_headers.EAVE_AUTHORIZATION_HEADER] = f"Bearer {self._access_token}"

        signature_message = payload
        if team_id is not None:
            headers[eave_headers.EAVE_TEAM_ID_HEADER] = team_id
            signature_message += team_id

        signature = signing.sign(
            signing_key=signing.get_key(signer=_ORIGIN.value),
            message=signature_message,
        )

        headers[eave_headers.EAVE_SIGNATURE_HEADER] = signature

        logger.debug(f"Eave Core API request: {method}\t{url}\t{headers}\t{payload}")

        async with aiohttp.ClientSession() as session:
            response = await session.request(
                method=method,
                url=url,
                headers=headers,
                data=payload,
            )

        if response.status == HTTPStatus.UNAUTHORIZED and use_auth:
            await self.refresh_access_token(
                input=operations.RefreshAccessToken.RequestBody(
                    access_token=self._access_token,
                    refresh_token=self._refresh_token,
                )
            )
            headers[eave_headers.EAVE_AUTHORIZATION_HEADER] = f"Bearer {self._access_token}"

            async with aiohttp.ClientSession() as session:
                response = await session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=payload,
                )

        logger.debug(f"Eave Core API response: {response}")
        return response

    @staticmethod
    def _makeurl(path: str) -> str:
        return urllib.parse.urljoin(shared_config.eave_api_base, path)

client = EaveCoreApiClient()