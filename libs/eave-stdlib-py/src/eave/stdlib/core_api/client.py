import typing
import urllib.parse
import uuid
from http import HTTPStatus
from typing import Optional
from uuid import UUID

import aiohttp
import eave.stdlib.eave_origins
import pydantic

from .. import exceptions as eave_exceptions
from .. import headers as eave_headers
from .. import logger, signing
from ..config import shared_config
from . import operations

_ORIGIN: eave.stdlib.eave_origins.EaveOrigin


def set_origin(origin: eave.stdlib.eave_origins.EaveOrigin) -> None:
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
        team_id=team_id,
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
        team_id=team_id,
    )

    response_json = await response.json()
    return operations.CreateSubscription.ResponseBody(**response_json)


async def delete_subscription(
    team_id: UUID,
    input: operations.DeleteSubscriptions.RequestBody,
) -> None:
    """
    POST /subscriptions/delete
    """
    await _make_request(
        path="/subscriptions/delete",
        input=input,
        team_id=team_id,
    )


async def get_subscriptions(
    team_id: UUID, input: operations.GetSubscriptions.RequestBody
) -> operations.GetSubscriptions.ResponseBody:
    """
    POST /subscriptions/query
    """
    response = await _make_request(
        path="/subscriptions/query",
        input=input,
        team_id=team_id,
    )

    response_json = await response.json()
    return operations.GetSubscriptions.ResponseBody(**response_json)


async def get_slack_installation(
    input: operations.GetSlackInstallation.RequestBody,
) -> operations.GetSlackInstallation.ResponseBody:
    """
    POST /integrations/slack/query
    """
    response = await _make_request(
        path="/integrations/slack/query",
        input=input,
    )

    response_json = await response.json()
    return operations.GetSlackInstallation.ResponseBody(**response_json)


async def get_github_installation(
    input: operations.GetGithubInstallation.RequestBody,
) -> operations.GetGithubInstallation.ResponseBody:
    """
    POST /integrations/github/query
    """
    response = await _make_request(
        path="/integrations/github/query",
        input=input,
    )

    response_json = await response.json()
    return operations.GetGithubInstallation.ResponseBody(**response_json)


async def get_atlassian_installation(
    input: operations.GetAtlassianInstallation.RequestBody,
) -> operations.GetAtlassianInstallation.ResponseBody:
    """
    POST /integrations/atlassian/query
    """
    response = await _make_request(
        path="/integrations/atlassian/query",
        input=input,
    )

    response_json = await response.json()
    return operations.GetAtlassianInstallation.ResponseBody(**response_json)


async def get_team(
    team_id: UUID,
) -> operations.GetAuthenticatedAccountTeamIntegrations.ResponseBody:
    """
    POST /team/query
    """
    response = await _make_request(
        path="/team/query",
        input=None,
        team_id=team_id,
    )

    response_json = await response.json()
    return operations.GetAuthenticatedAccountTeamIntegrations.ResponseBody(**response_json)


async def update_atlassian_integration(
    account_id: uuid.UUID,
    access_token: str,
    input: operations.UpdateAtlassianInstallation.RequestBody,
) -> operations.UpdateAtlassianInstallation.ResponseBody:
    """
    POST /me/team/integrations/atlassian/update
    """
    response = await _make_request(
        path="/me/team/integrations/atlassian/update",
        input=input,
        access_token=access_token,
        account_id=account_id,
    )

    response_json = await response.json()
    return operations.UpdateAtlassianInstallation.ResponseBody(**response_json)


async def get_authenticated_account_team_integrations(
    account_id: UUID, access_token: str
) -> operations.GetAuthenticatedAccountTeamIntegrations.ResponseBody:
    """
    POST /me/team/integrations/query
    """
    response = await _make_request(
        path="/me/team/integrations/query",
        input=None,
        access_token=access_token,
        account_id=account_id,
    )

    response_json = await response.json()
    return operations.GetAuthenticatedAccountTeamIntegrations.ResponseBody(**response_json)


async def get_authenticated_account(
    account_id: UUID, access_token: str
) -> operations.GetAuthenticatedAccount.ResponseBody:
    """
    POST /me/query
    """
    response = await _make_request(
        path="/me/query",
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
    logger.info(f"Eave Core API request", extra={"request_id": request_id, "method": method, "url": url})

    async with aiohttp.ClientSession() as session:
        response = await session.request(
            method=method,
            url=url,
            headers=headers,
            data=payload,
        )

    logger.info(
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


def makeurl(path: str) -> str:
    return urllib.parse.urljoin(shared_config.eave_api_base, path)


def build_message_to_sign(
    method: str,
    url: str,
    request_id: uuid.UUID,
    origin: eave.stdlib.eave_origins.EaveOrigin,
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
