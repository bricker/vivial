import urllib.parse
import uuid
from http import HTTPStatus
from typing import Optional
from uuid import UUID

import aiohttp
import pydantic
from eave.stdlib import eave_origins

from .. import exceptions as eave_exceptions
from .. import headers as eave_headers
from .. import logger, signing
from ..config import shared_config
from . import operations

_ORIGIN: eave_origins.EaveOrigin


def set_origin(origin: eave_origins.EaveOrigin) -> None:
    global _ORIGIN
    _ORIGIN = origin


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
) -> operations.GetSubscription.ResponseBody:
    """
    POST /subscriptions/query
    """
    response = await _make_request(
        path="/subscriptions/query",
        input=input,
        team_id=str(team_id),
    )

    response_json = await response.json()
    return operations.GetSubscription.ResponseBody(**response_json)


async def get_slack_installation(
    input: operations.GetSlackInstallation.RequestBody,
) -> operations.GetSlackInstallation.ResponseBody:
    """
    POST /installations/slack/query
    """
    # fetch slack bot details
    response = await _make_request(
        path="/installations/slack/query",
        input=input,
    )

    response_json = await response.json()
    return operations.GetSlackInstallation.ResponseBody(**response_json)


async def request_access_token(
    input: operations.RequestAccessToken.RequestBody,
) -> operations.RequestAccessToken.ResponseBody:
    """
    POST /auth/token/request
    """
    response = await _make_request(
        path="/auth/token/request",
        input=input,
    )

    response_json = await response.json()
    return operations.RequestAccessToken.ResponseBody(**response_json)


async def refresh_access_token(
    input: operations.RefreshAccessToken.RequestBody,
) -> operations.RefreshAccessToken.ResponseBody:
    """
    POST /auth/token/refresh
    """
    response = await _make_request(
        path="/auth/token/refresh",
        input=input,
        access_token=input.access_token,
    )

    response_json = await response.json()
    return operations.RefreshAccessToken.ResponseBody(**response_json)


async def _make_request(
    path: str,
    input: pydantic.BaseModel,
    method: str = "POST",
    access_token: Optional[str] = None,
    team_id: Optional[str] = None,
) -> aiohttp.ClientResponse:
    url = _makeurl(path)
    payload = input.json()
    request_id = str(uuid.uuid4())

    headers = {
        "content-type": "application/json",
        eave_headers.EAVE_ORIGIN_HEADER: _ORIGIN.value,
        eave_headers.EAVE_REQUEST_ID_HEADER: request_id,
    }

    if access_token:
        headers[eave_headers.EAVE_AUTHORIZATION_HEADER] = f"Bearer {access_token}"

    signature_message = payload
    if team_id is not None:
        headers[eave_headers.EAVE_TEAM_ID_HEADER] = team_id
        signature_message += team_id

    signature = signing.sign_b64(
        signing_key=signing.get_key(signer=_ORIGIN.value),
        data=signature_message,
    )

    headers[eave_headers.EAVE_SIGNATURE_HEADER] = signature

    logger.debug(f"Eave Core API request", extra={"request_id": request_id, "method": method, "url": url})

    async with aiohttp.ClientSession() as session:
        response = await session.request(
            method=method,
            url=url,
            headers=headers,
            data=payload,
        )

    logger.debug(
        f"Eave Core API response",
        extra={"request_id": request_id, "method": method, "url": url, "status": response.status},
    )

    try:
        response.raise_for_status()
    except aiohttp.ClientResponseError as e:
        match e.status:
            case HTTPStatus.NOT_FOUND:
                raise eave_exceptions.NotFoundError() from e
            case HTTPStatus.UNAUTHORIZED:
                raise eave_exceptions.UnauthorizedError() from e
            case HTTPStatus.BAD_REQUEST:
                raise eave_exceptions.BadRequestError() from e
            case HTTPStatus.INTERNAL_SERVER_ERROR:
                raise eave_exceptions.InternalServerError() from e
            case _:
                raise eave_exceptions.HTTPException(status_code=e.status) from e

    return response


def _makeurl(path: str) -> str:
    return urllib.parse.urljoin(shared_config.eave_api_base, path)
