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


async def delete_subscription(
    team_id: UUID,
    input: operations.DeleteSubscription.RequestBody,
) -> None:
    """
    POST /subscriptions/delete
    """
    await _make_request(
        path="/subscriptions/delete",
        input=input,
        team_id=str(team_id),
    )


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

# TODO: add team_id
async def get_slack_installation(
    team_id: UUID,
    input: operations.GetSlackInstallation.RequestBody,
) -> Optional[operations.GetSlackInstallation.ResponseBody]:
    """
    POST /installations/slack/query
    """
    # fetch slack bot details
    response = await _make_request(
        path="/installations/slack/query",
        input=input,
        team_id=str(team_id),
    )

    if response.status >= 300:
        return None

    response_json = await response.json()
    return operations.GetSlackInstallation.ResponseBody(**response_json)

async def get_available_sources(
    team_id: UUID,
    input: operations.GetAvailableSources.RequestBody,
) -> Optional[operations.GetAvailableSources.ResponseBody]:
    """
    POST TODO somewhere
    """
    response = await _make_request(
        path="/TODO",
        input=input,
        team_id=str(team_id),
    )

    if response.status >= 300:
        return None

    response_json = await response.json()
    return operations.GetAvailableSources.ResponseBody(**response_json)

def _makeurl(path: str) -> str:
    return urllib.parse.urljoin(shared_config.eave_api_base, path)


async def _make_request(path: str, input: pydantic.BaseModel, team_id: Optional[str]) -> aiohttp.ClientResponse:
    payload = input.json()
    signature = signing.sign(
        payload=payload,
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
    payload = input.json()
    logger.debug(f"Eave Core API request: {method}\t{url}\t{headers}\t{payload}")

    async with aiohttp.ClientSession() as session:
        response = await session.request(
            method=method,
            url=url,
            headers=headers,
            data=payload,
        )

    logger.debug(f"Eave Core API response: {response}")
    return response
