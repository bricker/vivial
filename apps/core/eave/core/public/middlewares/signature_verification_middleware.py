import uuid
from typing import Set, cast

import eave.core.public.requests.util as request_util
import eave.stdlib.core_api.client
import eave.stdlib.exceptions as eave_exceptions
import eave.stdlib.headers as eave_headers
import eave.stdlib.signing as eave_signing
from eave.stdlib import logger

from . import EaveASGIMiddleware, _development_bypass, asgi_types

_ROUTE_BYPASS: Set[str] = set()


def add_bypass(path: str) -> None:
    global _ROUTE_BYPASS
    _ROUTE_BYPASS.add(path)


class SignatureVerificationASGIMiddleware(EaveASGIMiddleware):
    """
    Reads the body and headers and verifies the signature.
    Note that this middleware necessarily blocks the request until the full body is received,
    so that it can calculate the expected signature and compare it to the provided signature.
    """

    async def __call__(
        self, scope: asgi_types.Scope, receive: asgi_types.ASGIReceiveCallable, send: asgi_types.ASGISendCallable
    ) -> None:
        if scope["type"] != "http" or scope["path"] in _ROUTE_BYPASS:
            await self.app(scope, receive, send)
            return

        if _development_bypass.development_bypass_allowed(scope=scope):
            logger.warning("Bypassing signature verification in dev environment")
            await self.app(scope, receive, send)
            return

        body: bytes = b""

        while True:
            # https://asgi.readthedocs.io/en/latest/specs/www.html#request-receive-event
            message = await receive()
            assert message["type"] == "http.request"
            chunk: bytes = message.get("body", b"")
            body += chunk

            if message.get("more_body", False) is False:
                break

        # This cast was necessary, the type checker wasn't picking up that `scope` had been implicitly cast
        # to HTTPScope at the beginning of the function.
        self._do_signature_verification(scope=cast(asgi_types.HTTPScope, scope), body=body)

        async def dummy_receive() -> asgi_types.ASGIReceiveEvent:
            return {
                "type": "http.request",
                "body": body,
                "more_body": False,
            }

        await self.app(scope, dummy_receive, send)

    @staticmethod
    def _do_signature_verification(scope: asgi_types.HTTPScope, body: bytes) -> None:
        eave_state = request_util.get_eave_state(scope=scope)

        signature = request_util.get_header_value(scope=scope, name=eave_headers.EAVE_SIGNATURE_HEADER)
        if not signature:
            # reject None or empty strings
            logger.error("missing signature", extra=eave_state.log_context)
            raise eave_exceptions.MissingRequiredHeaderError("eave-signature")

        payload = body.decode()
        team_id_header = request_util.get_header_value(scope=scope, name=eave_headers.EAVE_TEAM_ID_HEADER)
        account_id_header = request_util.get_header_value(scope=scope, name=eave_headers.EAVE_ACCOUNT_ID_HEADER)

        team_id = uuid.UUID(team_id_header) if team_id_header else None
        account_id = uuid.UUID(account_id_header) if account_id_header else None

        message = eave.stdlib.core_api.client.build_message_to_sign(
            method=scope["method"],
            url=eave.stdlib.core_api.client.makeurl(scope["path"]),
            request_id=eave_state.request_id,
            origin=eave_state.eave_origin,
            team_id=team_id,
            account_id=account_id,
            payload=payload,
        )

        signing_key = eave_signing.get_key(signer=eave_state.eave_origin)

        eave_signing.verify_signature_or_exception(
            signing_key=signing_key,
            message=message,
            signature=signature,
        )
