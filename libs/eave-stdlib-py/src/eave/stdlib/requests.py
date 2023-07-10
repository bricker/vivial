import pydantic
from typing import NotRequired, Optional, Required, TypedDict, Unpack
import uuid
import aiohttp
from eave.stdlib.eave_origins import EaveOrigin
from eave.stdlib.typing import JsonObject

from eave.stdlib.util import ensure_str_or_none, redact

from . import headers as eave_headers
from . import signing
from .logging import LogContext, eaveLogger


class CommonRequestArgs(TypedDict):
    origin: Required[EaveOrigin]
    method: NotRequired[str]
    addl_headers: NotRequired[Optional[dict[str, str]]]
    ctx: NotRequired[Optional[LogContext]]
    base_timeout_seconds: NotRequired[int]


async def make_request(
    url: str,
    input: Optional[pydantic.BaseModel],
    team_id: Optional[uuid.UUID | str] = None,
    access_token: Optional[str] = None,
    account_id: Optional[uuid.UUID | str] = None,
    **kwargs: Unpack[CommonRequestArgs],
) -> aiohttp.ClientResponse:
    origin = kwargs["origin"]
    ctx = kwargs.get("ctx")
    method = kwargs.get("method", "POST")
    addl_headers = kwargs.get("addl_headers", {})
    base_timeout_seconds = kwargs.get("base_timeout_seconds", 600)

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

    signature_message = signing.build_message_to_sign(
        method=method,
        url=url,
        request_id=request_id,
        origin=origin.value,
        team_id=team_id,
        account_id=account_id,
        payload=payload,
        ctx=ctx,
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
