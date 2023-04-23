from http import HTTPStatus
from typing import Any, Awaitable, Callable, List, Set
import fastapi
from starlette.middleware.base import BaseHTTPMiddleware
import eave.core.public.requests.util as request_util
import eave.stdlib.signing as eave_signing
import eave.stdlib.exceptions as eave_errors
import apps.core.eave.core.public.requests.state as eave_state
import eave.stdlib.core_api.headers as eave_headers
from . import EaveMiddleware
from eave.stdlib import logger

_BYPASS: Set[str] = set()

def add_bypass(path: str) -> None:
    global _BYPASS
    _BYPASS.add(path)

class ValidateSignatureMiddleware(EaveMiddleware):
    async def dispatch(self, request: fastapi.Request, call_next: Callable[[fastapi.Request], Awaitable[fastapi.Response]]) -> fastapi.Response:
        global _BYPASS
        if request.url.path not in _BYPASS:
            state = eave_state.EaveRequestState(request.state)
            body = await request.body()
            payload = body.decode()
            signature = request.headers.get(eave_headers.EAVE_SIGNATURE_HEADER)

            if not signature or not payload:
                # reject None or empty strings
                logger.error("signature or payload missing/empty", extra=request_util.log_context(request))
                raise fastapi.HTTPException(HTTPStatus.BAD_REQUEST)

            message = payload
            if (team_id := request.headers.get(eave_headers.EAVE_TEAM_ID_HEADER)) is not None:
                message += team_id

            signing_key = eave_signing.get_key(signer=state.eave_origin.value)
            eave_signing.validate_signature_or_exception(
                signing_key=signing_key,
                message=payload,
                signature=signature,
            )

        response = await call_next(request)
        return response
