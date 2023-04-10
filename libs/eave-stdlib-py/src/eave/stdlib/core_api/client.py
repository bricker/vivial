import urllib.parse
from typing import Optional
from uuid import UUID

import aiohttp
import pydantic

from .. import logger
from ..config import shared_config
from . import operations, signing


async def status() -> operations.Status.ResponseBody:
    async with aiohttp.ClientSession() as session:
        response = await session.request(
            "GET",
            _makeurl("/status"),
        )

    response_json = await response.json()
    return operations.Status.ResponseBody(**response_json)


async def create_access_request(
    input: operations.CreateAccessRequest.RequestBody,
) -> None:
    """
    POST /access_request
    """
    await _make_request(
        path="/access_request",
        input=input,
        team_id=None,
    )

    return None


async def upsert_document(
    team_id: UUID,
    input: operations.UpsertDocument.RequestBody,
) -> operations.UpsertDocument.ResponseBody:
    """
    POST /documents/upsert
    """
    response = await _make_request(
        path="/documents/upsert",
        input=input,
        team_id=str(team_id),
    )

    response_json = await response.json()
    return operations.UpsertDocument.ResponseBody(**response_json)


async def create_subscription(
    team_id: UUID,
    input: operations.CreateSubscription.RequestBody,
) -> operations.CreateSubscription.ResponseBody:
    """
    POST /subscriptions/create
    """
    response = await _make_request(
        path="/subscriptions/create",
        input=input,
        team_id=str(team_id),
    )

    response_json = await response.json()
    return operations.CreateSubscription.ResponseBody(**response_json)


async def get_subscription(
    team_id: UUID, input: operations.GetSubscription.RequestBody
) -> Optional[operations.GetSubscription.ResponseBody]:
    """
    POST /subscriptions/query
    """
    response = await _make_request(
        path="/subscriptions/query",
        input=input,
        team_id=str(team_id),
    )

    if response.status >= 300:
        return None

    response_json = await response.json()
    return operations.GetSubscription.ResponseBody(**response_json)


# TODO: need eave teamid input?
async def get_slack_source(
    input: operations.GetSlackSource.RequestBody,
) -> Optional[operations.GetSlackSource.ResponseBody]:
    """
    POST /slack_sources/query
    """
    # fetch slack bot details
    response = await _make_request(
        path="/slack_sources/query",
        input=input,
        team_id=None,
    )

    if response.status >= 300:
        # TODO: log?
        return None

    response_json = await response.json()
    return operations.GetSlackSource.ResponseBody(**response_json)


def _makeurl(path: str) -> str:
    return urllib.parse.urljoin(shared_config.eave_api_base, path)


async def _make_request(path: str, input: pydantic.BaseModel, team_id: Optional[str]) -> aiohttp.ClientResponse:
    signature = signing.sign(
        payload=input.json(),
        team_id=team_id,
    )

    headers = {
        "content-type": "application/json",
        signing.SIGNATURE_HEADER_NAME: signature,
        "Content-Type": "application/json",
    }

    if team_id is not None:
        headers[signing.TEAM_ID_HEADER_NAME] = team_id

    method = "POST"
    url = _makeurl(path)
    logger.debug(f"Eave Core API request: {method}\t{url}\t{headers}\t{payload}")

    async with aiohttp.ClientSession() as session:
        response = await session.request(
            method=method,
            url=url,
            headers=headers,
            data=input.json(),
        )

    logger.debug(f"Eave Core API response: {response}")
    return response
