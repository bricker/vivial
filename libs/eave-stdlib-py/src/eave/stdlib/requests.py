import pydantic
from typing import NotRequired, Optional, Required, TypedDict, Unpack
import uuid
import aiohttp
from eave.stdlib.core_api.operations import EndpointConfiguration
from eave.stdlib.eave_origins import EaveApp
from eave.stdlib.typing import JsonObject

from eave.stdlib.util import ensure_str_or_none, redact

from . import headers as eave_headers
from . import signing
from .logging import LogContext, eaveLogger


class CommonRequestArgs(TypedDict):
    origin: Required[EaveApp]
    addl_headers: NotRequired[Optional[dict[str, str]]]
    ctx: NotRequired[Optional[LogContext]]
    base_timeout_seconds: NotRequired[int]


class MissingParameterError(Exception):
    pass


async def make_request(
    config: EndpointConfiguration,
    input: Optional[pydantic.BaseModel],
    team_id: Optional[uuid.UUID | str] = None,
    access_token: Optional[str] = None,
    account_id: Optional[uuid.UUID | str] = None,
    **kwargs: Unpack[CommonRequestArgs],
) -> aiohttp.ClientResponse:
    base_timeout_seconds = kwargs.get("base_timeout_seconds", 600)
    ctx = LogContext.wrap(kwargs.get("ctx"))
    origin = kwargs["origin"]
    addl_headers = kwargs.get("addl_headers", {}) or {}
    # The indent and separators params here ensure that the payload is as compact as possible.
    # It's mostly a way to normalize the payload so services know what to expect.
    payload = (
        input.json(exclude_unset=True, indent=None, separators=(",", ":"))
        if input
        else "{}"
    )  # empty JSON object

    headers, request_params = build_headers(
        config=config,
        payload=payload,
        ctx=ctx,
        team_id=team_id,
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

    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=base_timeout_seconds)
    ) as session:
        response = await session.request(
            method=config.method,
            url=config.url,
            headers=headers,
            data=payload,
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
    payload: str,
    origin: EaveApp,
    addl_headers: dict[str, str],
    team_id: Optional[uuid.UUID | str] = None,
    access_token: Optional[str] = None,
    account_id: Optional[uuid.UUID | str] = None,
    ctx: Optional[LogContext] = None,
) -> tuple[dict[str, str], JsonObject]:
    """
    Constructs Eave core api auth headers as required by `config`.

    returns tuple of headers dict, followed by JsonObject used to debug logging.
    """
    ctx = LogContext.wrap(ctx=ctx)
    request_id = ctx.eave_request_id
    eave_sig_ts = signing.make_sig_ts()

    headers: dict[str, str] = {
        eave_headers.EAVE_ORIGIN_HEADER: origin.value,
        eave_headers.EAVE_REQUEST_ID_HEADER: request_id,
        eave_headers.EAVE_SIG_TS_HEADER: str(eave_sig_ts),
    }

    if access_token:
        headers[aiohttp.hdrs.AUTHORIZATION] = f"Bearer {access_token}"

    team_id = team_id or ctx.eave_team_id
    if team_id:
        headers[eave_headers.EAVE_TEAM_ID_HEADER] = str(team_id)

    account_id = account_id or ctx.eave_account_id
    if account_id:
        headers[eave_headers.EAVE_ACCOUNT_ID_HEADER] = str(account_id)

    signature_message = signing.build_message_to_sign(
        method=config.method,
        path=config.path,
        request_id=request_id,
        origin=origin,
        audience=config.audience,
        ts=eave_sig_ts,
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
        "eave_audience": config.audience.value,
        "eave_team_id": ensure_str_or_none(team_id),
        "eave_account_id": ensure_str_or_none(account_id),
        "method": config.method,
        "url": config.url,
    }

    return (headers, request_params)
