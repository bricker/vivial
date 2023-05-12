import pydantic
from typing import Optional
import uuid
import aiohttp
import urllib.parse
from http import HTTPStatus
from .. import exceptions as eave_exceptions
from .. import headers as eave_headers
from .. import logger, signing
from ..config import shared_config
from .. import eave_origins as eave_origins


_ORIGIN: eave_origins.EaveOrigin


def set_origin(origin: eave_origins.EaveOrigin) -> None:
    global _ORIGIN
    _ORIGIN = origin


async def make_request(
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
    team_id: Optional[uuid.UUID],
    account_id: Optional[uuid.UUID],
) -> str:
    signature_elements: list[str] = [
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
