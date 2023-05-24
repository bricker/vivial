import pydantic
from typing import Optional
import uuid
import aiohttp
import urllib.parse
from http import HTTPStatus

from eave.stdlib.util import redact

from . import exceptions as eave_exceptions
from . import headers as eave_headers
from . import signing
from .logging import eaveLogger
from .config import shared_config
from . import eave_origins as eave_origins


_ORIGIN: eave_origins.EaveOrigin


def set_origin(origin: eave_origins.EaveOrigin) -> None:
    global _ORIGIN
    _ORIGIN = origin


async def make_request(
    url: str,
    input: Optional[pydantic.BaseModel],
    method: str = "POST",
    access_token: Optional[str] = None,
    team_id: Optional[uuid.UUID] = None,
    account_id: Optional[uuid.UUID] = None,
) -> aiohttp.ClientResponse:
    request_id = str(uuid.uuid4())

    headers = {
        eave_headers.CONTENT_TYPE: "application/json",
        eave_headers.EAVE_ORIGIN_HEADER: _ORIGIN.value,
        eave_headers.EAVE_REQUEST_ID_HEADER: str(request_id),
    }

    payload = input.json() if input else ""

    if access_token:
        headers[eave_headers.AUTHORIZATION_HEADER] = f"Bearer {access_token}"

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
    eaveLogger.info(
        f"Eave Client Request: {request_id}: {method} {url}",
        extra={
            "json_fields": {
                "signature": redact(signature),
                "access_token": redact(access_token),
                "origin": _ORIGIN.value,
                "team_id": str(team_id),
                "account_id": str(account_id),
                "request_id": request_id,
                "method": method,
                "url": url,
            }
        },
    )

    async with aiohttp.ClientSession() as session:
        response = await session.request(
            method=method,
            url=url,
            headers=headers,
            data=payload,
        )

        # Consume the body while the session is still open
        await response.read()

    eaveLogger.info(
        f"Eave Client Response: {request_id}: {method} {url}",
        extra={
            "json_fields": {
                "signature": redact(signature),
                "access_token": redact(access_token),
                "origin": _ORIGIN.value,
                "team_id": str(team_id),
                "account_id": str(account_id),
                "request_id": request_id,
                "method": method,
                "url": url,
                "status": response.status,
            }
        },
    )

    try:
        response.raise_for_status()
    except aiohttp.ClientResponseError as e:
        match e.status:
            case HTTPStatus.NOT_FOUND:
                raise eave_exceptions.NotFoundError(request_id=request_id)
            case HTTPStatus.UNAUTHORIZED:
                raise eave_exceptions.UnauthorizedError(request_id=request_id)
            case HTTPStatus.BAD_REQUEST:
                raise eave_exceptions.BadRequestError(request_id=request_id)
            case HTTPStatus.INTERNAL_SERVER_ERROR:
                raise eave_exceptions.InternalServerError(request_id=request_id)
            case _:
                raise eave_exceptions.HTTPException(status_code=e.status)

    return response


def makeurl(path: str, base: Optional[str] = None) -> str:
    if not base:
        base = shared_config.eave_api_base
    return urllib.parse.urljoin(base, path)


def build_message_to_sign(
    method: str,
    url: str,
    request_id: uuid.UUID | str,
    origin: eave_origins.EaveOrigin | str,
    payload: str,
    team_id: Optional[uuid.UUID | str],
    account_id: Optional[uuid.UUID | str],
) -> str:
    signature_elements: list[str] = [
        origin,
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
