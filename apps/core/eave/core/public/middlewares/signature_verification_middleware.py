from http import HTTPStatus
from typing import Set, cast
import fastapi
import eave.core.public.requests.util as request_util
import eave.stdlib.signing as eave_signing
import eave.stdlib.core_api.headers as eave_headers
import eave.stdlib.exceptions as eave_exceptions
from . import EaveASGIMiddleware, asgi_types
from eave.stdlib import logger

_BYPASS: Set[str] = set()

def add_bypass(path: str) -> None:
    global _BYPASS
    _BYPASS.add(path)

class SignatureVerificationASGIMiddleware(EaveASGIMiddleware):
    async def process(self, scope: asgi_types.Scope, receive: asgi_types.ASGIReceiveCallable, send: asgi_types.ASGISendCallable) -> None:
        if scope["type"] != "http" or scope["path"] in _BYPASS:
            await self.app(scope, receive, send)
            return

        body: bytes = b""

        async def wrapped_receive() -> asgi_types.ASGIReceiveEvent:
            nonlocal body
            # https://asgi.readthedocs.io/en/latest/specs/www.html#request-receive-event
            message = await receive()
            assert message["type"] == "http.request"
            chunk: bytes = message.get("body", b"")
            body += chunk

            if message.get("more_body", False) is False:
                # This cast was necessary, the type checker wasn't picking up that `scope` had been implicitly cast
                # to HTTPScope at the beginning of the function.
                self._do_signature_verification(scope=cast(asgi_types.HTTPScope, scope), body=body)

            return message

        await self.app(scope, wrapped_receive, send)

    @staticmethod
    def _do_signature_verification(scope: asgi_types.HTTPScope, body: bytes) -> None:
        payload = body.decode()
        signature = request_util.get_header_value(scope=scope, name=eave_headers.EAVE_SIGNATURE_HEADER)

        if not signature or not payload:
            # reject None or empty strings
            logger.error("signature or payload missing/empty", extra=request_util.log_context(scope))
            raise eave_exceptions.MissingRequiredHeaderError("eave-signature")

        message = payload
        team_id = request_util.get_header_value(scope=scope, name=eave_headers.EAVE_TEAM_ID_HEADER)
        if team_id is not None:
            message += team_id

        origin = request_util.get_eave_state(scope=scope).eave_origin.value
        signing_key = eave_signing.get_key(signer=origin)
        eave_signing.verify_signature_or_exception(
            signing_key=signing_key,
            message=message,
            signature=signature,
        )
