import typing
import urllib.parse
import uuid
from http import HTTPStatus
from typing import Optional
from uuid import UUID

import aiohttp
import pydantic

from .. import eave_origins as eave_origins
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
            makeurl("/status"),
        )

    response_json = await response.json()
    return operations.Status.ResponseBody(**response_json)

async def upsert_document(
    team_id: UUID,
    input: operations.UpsertDocument.RequestBody,
) -> operations.UpsertDocument.ResponseBody:
    response = await _make_request(
        path=operations.UpsertDocument.config.path,
        input=input,
        team_id=team_id,
    )

    response_json = await response.json()
    return operations.UpsertDocument.ResponseBody(**response_json)


async def create_subscription(
    team_id: UUID,
    input: operations.CreateSubscription.RequestBody,
) -> operations.CreateSubscription.ResponseBody:
    response = await _make_request(
        path=operations.CreateSubscription.config.path,
        input=input,
        team_id=team_id,
    )

    response_json = await response.json()
    return operations.CreateSubscription.ResponseBody(**response_json)


async def delete_subscription(
    team_id: UUID,
    input: operations.DeleteSubscription.RequestBody,
) -> None:
    await _make_request(
        path=operations.DeleteSubscription.config.path,
        input=input,
        team_id=team_id,
    )


async def get_subscription(
    team_id: UUID, input: operations.GetSubscription.RequestBody
) -> operations.GetSubscription.ResponseBody:
    response = await _make_request(
        path=operations.GetSubscription.config.path,
        input=input,
        team_id=team_id,
    )

    response_json = await response.json()
    return operations.GetSubscription.ResponseBody(**response_json)


async def get_slack_installation(
    input: operations.GetSlackInstallation.RequestBody,
) -> operations.GetSlackInstallation.ResponseBody:
    response = await _make_request(
        path=operations.GetSlackInstallation.config.path,
        input=input,
    )

    response_json = await response.json()
    return operations.GetSlackInstallation.ResponseBody(**response_json)


async def get_github_installation(
    input: operations.GetGithubInstallation.RequestBody,
) -> operations.GetGithubInstallation.ResponseBody:
    response = await _make_request(
        path=operations.GetGithubInstallation.config.path,
        input=input,
    )

    response_json = await response.json()
    return operations.GetGithubInstallation.ResponseBody(**response_json)


async def query_forge_installation(
    input: operations.forge.QueryForgeInstallation.RequestBody,
) -> operations.forge.QueryForgeInstallation.ResponseBody:
    response = await _make_request(
        path=operations.forge.QueryForgeInstallation.config.path,
        input=input,
    )

    response_json = await response.json()
    return operations.forge.QueryForgeInstallation.ResponseBody(**response_json)


async def register_forge_installation(
    input: operations.forge.RegisterForgeInstallation.RequestBody,
) -> operations.forge.RegisterForgeInstallation.ResponseBody:
    response = await _make_request(
        path=operations.forge.RegisterForgeInstallation.config.path,
        input=input,
    )

    response_json = await response.json()
    return operations.forge.RegisterForgeInstallation.ResponseBody(**response_json)

async def update_forge_installation_authed(
    account_id: uuid.UUID,
    access_token: str,
    input: operations.forge.UpdateForgeInstallation.RequestBody,
) -> operations.forge.UpdateForgeInstallation.ResponseBody:
    response = await _make_request(
        path=operations.forge.UpdateForgeInstallation.config.path,
        input=input,
        access_token=access_token,
        account_id=account_id,
    )

    response_json = await response.json()
    return operations.forge.UpdateForgeInstallation.ResponseBody(**response_json)


async def get_team(
    team_id: UUID,
) -> operations.GetAuthenticatedAccountTeamIntegrations.ResponseBody:
    response = await _make_request(
        path=operations.GetAuthenticatedAccountTeamIntegrations.config.path,
        input=None,
        team_id=team_id,
    )

    response_json = await response.json()
    return operations.GetAuthenticatedAccountTeamIntegrations.ResponseBody(**response_json)



async def get_authenticated_account_team_integrations(
    account_id: UUID, access_token: str
) -> operations.GetAuthenticatedAccountTeamIntegrations.ResponseBody:
    response = await _make_request(
        path=operations.GetAuthenticatedAccountTeamIntegrations.config.path,
        input=None,
        access_token=access_token,
        account_id=account_id,
    )

    response_json = await response.json()
    return operations.GetAuthenticatedAccountTeamIntegrations.ResponseBody(**response_json)


async def get_authenticated_account(
    account_id: UUID, access_token: str
) -> operations.GetAuthenticatedAccount.ResponseBody:
    response = await _make_request(
        path=operations.GetAuthenticatedAccount.config.path,
        input=None,
        access_token=access_token,
        account_id=account_id,
    )

    response_json = await response.json()
    return operations.GetAuthenticatedAccount.ResponseBody(**response_json)


async def _make_request(
    path: str,
    input: Optional[pydantic.BaseModel],
    method: str = "POST",
    access_token: Optional[str] = None,
    team_id: Optional[uuid.UUID] = None,
    account_id: Optional[uuid.UUID] = None,
) -> aiohttp.ClientResponse:
    url = makeurl(path)
    request_id = uuid.uuid4()

    headers = {
        "content-type": "application/json",
        eave_headers.EAVE_ORIGIN_HEADER: _ORIGIN.value,
        eave_headers.EAVE_REQUEST_ID_HEADER: str(request_id),
    }

    payload = input.json() if input else ""

    if access_token:
        headers[eave_headers.EAVE_AUTHORIZATION_HEADER] = f"Bearer {access_token}"

    if team_id:
        headers[eave_headers.EAVE_TEAM_ID_HEADER] = str(team_id)

    if account_id:
        headers[eave_headers.EAVE_ACCOUNT_ID_HEADER] = str(account_id)

    signature_message = build_message_to_sign(
        method=method,
        url=url,
        request_id=request_id,
        origin=_ORIGIN,
        team_id=team_id,
        account_id=account_id,
        payload=payload,
    )

    signature = signing.sign_b64(
        signing_key=signing.get_key(signer=_ORIGIN.value),
        data=signature_message,
    )

    headers[eave_headers.EAVE_SIGNATURE_HEADER] = signature
    logger.info("Eave Core API request", extra={"request_id": request_id, "method": method, "url": url})

    async with aiohttp.ClientSession() as session:
        response = await session.request(
            method=method,
            url=url,
            headers=headers,
            data=payload,
        )

    logger.info(
        "Eave Core API response",
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


def makeurl(path: str) -> str:
    return urllib.parse.urljoin(shared_config.eave_api_base, path)


def build_message_to_sign(
    method: str,
    url: str,
    request_id: uuid.UUID,
    origin: eave_origins.EaveOrigin,
    payload: str,
    team_id: typing.Optional[uuid.UUID],
    account_id: typing.Optional[uuid.UUID],
) -> str:
    signature_elements: typing.List[str] = [
        origin.value,
        method,
        url,
        str(request_id),
        payload,
    ]

    if team_id:
        signature_elements.append(str(team_id))

    if account_id:
        signature_elements.append(str(account_id))

    signature_message = ":".join(signature_elements)

    return signature_message
