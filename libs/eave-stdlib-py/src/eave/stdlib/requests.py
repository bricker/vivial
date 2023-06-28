import pydantic
from typing import Generic, NotRequired, Optional, Required, TypeVar, TypedDict
import uuid
import aiohttp
import urllib.parse
from eave.stdlib.eave_origins import EaveOrigin, EaveService
from eave.stdlib.typing import JsonObject

from eave.stdlib.util import ensure_str_or_none, redact

from . import headers as eave_headers
from . import signing
from .logging import LogContext, eaveLogger
from .config import shared_config

IT = TypeVar("IT", bound=pydantic.BaseModel)

class CommonRequestArgs(TypedDict):
    origin: Required[EaveOrigin]
    method: NotRequired[str]
    addl_headers: NotRequired[Optional[dict[str, str]]]
    ctx: NotRequired[Optional[LogContext]]
    base_timeout_seconds: NotRequired[int]

async def make_request(
    url: str,
    origin: EaveOrigin,
    input: Optional[pydantic.BaseModel],
    method: str = "POST",
    team_id: Optional[uuid.UUID | str] = None,
    access_token: Optional[str] = None,
    account_id: Optional[uuid.UUID | str] = None,
    addl_headers: Optional[dict[str, str]] = None,
    ctx: Optional[LogContext] = None,
    base_timeout_seconds: int = 600, # system-imposed AppEngine request timeout
) -> aiohttp.ClientResponse:
    ctx = LogContext.wrap(ctx)
    request_id = ctx.eave_request_id

    headers: dict[str, str] = {
        eave_headers.CONTENT_TYPE: "application/json",
        eave_headers.EAVE_ORIGIN_HEADER: origin.value,
        eave_headers.EAVE_REQUEST_ID_HEADER: request_id,
    }

    # The indent and separators params here ensure that the payload is as compact as possible.
    # It's mostly a way to normalize the payload so services know what to expect.
    payload = input.json(indent=None, separators=(",", ":")) if input else "{}"  # empty JSON object

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
        origin=origin.value,
        team_id=team_id,
        account_id=account_id,
        payload=payload,
    )

    signature = signing.sign_b64(
        signing_key=signing.get_key(signer=origin.value),
        data=signature_message,
        ctx=ctx,
    )

    headers[eave_headers.EAVE_SIGNATURE_HEADER] = signature

    if addl_headers:
        headers.update(addl_headers)

    request_params: JsonObject = {
        "signature": redact(signature),
        "access_token": redact(access_token),
        "eave_request_id": request_id,
        "eave_origin": origin.value,
        "eave_team_id": ensure_str_or_none(team_id),
        "eave_account_id": ensure_str_or_none(account_id),
        "method": method,
        "url": url,
    }

    eaveLogger.info(
        f"Client Request: {request_id}: {method} {url}",
        ctx,
        request_params,
    )

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=base_timeout_seconds)) as session:
        response = await session.request(
            method=method,
            url=url,
            headers=headers,
            data=payload,
        )

        # Consume the body while the session is still open
        await response.read()

    eaveLogger.info(
        f"Client Response: {request_id}: {method} {url}",
        ctx,
        request_params,
        {"status": response.status},
    )

    response.raise_for_status()
    return response


def makeurl(path: str, base: Optional[str] = None) -> str:
    if not base:
        base = shared_config.eave_public_api_base
    return urllib.parse.urljoin(base, path)


def build_message_to_sign(
    method: str,
    url: str,
    request_id: uuid.UUID | str,
    origin: EaveOrigin | str,
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
