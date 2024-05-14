import uuid
from typing import NotRequired, Required, TypedDict, Unpack

import aiohttp
import pydantic

from eave.stdlib.core_api.operations import EndpointConfiguration
from eave.stdlib.eave_origins import EaveApp
from eave.stdlib.typing import JsonObject
from eave.stdlib.util import ensure_str_or_none, redact

from . import headers as eave_headers
from .logging import LogContext, eaveLogger


class CommonRequestArgs(TypedDict):
    origin: Required[EaveApp]
    addl_headers: NotRequired[dict[str, str] | None]
    ctx: NotRequired[LogContext]
    base_timeout_seconds: NotRequired[int]


class MissingParameterError(Exception):
    pass


async def make_request(
    *,
    config: EndpointConfiguration,
    input: pydantic.BaseModel | None,
    access_token: str | None = None,
    account_id: uuid.UUID | str | None = None,
    allow_redirects: bool = True,
    **kwargs: Unpack[CommonRequestArgs],
) -> aiohttp.ClientResponse:
    base_timeout_seconds = kwargs.get("base_timeout_seconds", 600)
    origin = kwargs["origin"]
    addl_headers = kwargs.get("addl_headers", {}) or {}
    ctx = kwargs.get("ctx", LogContext())

    # The indent and separators params here ensure that the payload is as compact as possible.
    # It's mostly a way to normalize the payload so services know what to expect.
    payload = input.json(exclude_unset=True, indent=None, separators=(",", ":")) if input else "{}"  # empty JSON object

    headers, request_params = build_headers(
        config=config,
        ctx=ctx,
        access_token=access_token,
        account_id=account_id,
        origin=origin,
        addl_headers=addl_headers,
    )
    headers[aiohttp.hdrs.CONTENT_TYPE] = eave_headers.MIME_TYPE_JSON

    eaveLogger.info(
        f"Client Request: {ctx.eave_request_id}: {config.method} {config.path}",
        ctx,
        request_params,
    )

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=base_timeout_seconds)) as session:
        response = await session.request(
            method=config.method,
            url=config.url,
            headers=headers,
            data=payload,
            allow_redirects=allow_redirects,
        )

        # Consume the body while the session is still open
        await response.read()

    eaveLogger.info(
        f"Client Response: {ctx.eave_request_id}: {config.method} {config.url}",
        ctx,
        request_params,
        {"status": response.status},
    )

    response.raise_for_status()
    return response


def build_headers(
    config: EndpointConfiguration,
    origin: EaveApp,
    addl_headers: dict[str, str],
    ctx: LogContext,
    access_token: str | None = None,
    account_id: uuid.UUID | str | None = None,
) -> tuple[dict[str, str], JsonObject]:
    """
    Constructs Eave core api auth headers as required by `config`.

    returns tuple of headers dict, followed by JsonObject used to debug logging.
    """
    request_id = ctx.eave_request_id

    headers: dict[str, str] = {
        eave_headers.EAVE_ORIGIN_HEADER: origin.value,
        eave_headers.EAVE_REQUEST_ID_HEADER: request_id,
    }

    request_params: JsonObject = {
        "eave_request_id": request_id,
        "eave_origin": origin.value,
        "eave_audience": config.audience.value,
        "method": config.method,
        "url": config.url,
    }

    if config.auth_required:
        if not access_token:
            raise ValueError("missing access_token")
        headers[aiohttp.hdrs.AUTHORIZATION] = f"Bearer {access_token}"
        request_params["access_token"] = redact(access_token)

        account_id = account_id or ctx.eave_authed_account_id
        if not account_id:
            raise ValueError("missing account_id")
        headers[eave_headers.EAVE_ACCOUNT_ID_HEADER] = str(account_id)
        request_params["eave_account_id"] = ensure_str_or_none(account_id)

    if addl_headers:
        headers.update(addl_headers)

    return (headers, request_params)
