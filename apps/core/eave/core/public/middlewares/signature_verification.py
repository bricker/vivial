import eave.stdlib
import eave.stdlib.request_state
import eave.stdlib.requests
from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, HTTPScope, Scope

from eave.stdlib.middleware.base import EaveASGIMiddleware
from . import development_bypass
from eave.stdlib.logging import eaveLogger


class SignatureVerificationASGIMiddleware(EaveASGIMiddleware):
    """
    Reads the body and headers and verifies the signature.
    Note that this middleware necessarily blocks the request until the full body is received,
    so that it can calculate the expected signature and compare it to the provided signature.
    """

    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if development_bypass.development_bypass_allowed(scope=scope):
            eaveLogger.warning("Bypassing signature verification in dev environment")
            await self.app(scope, receive, send)
            return

        body = await self.read_body(scope=scope, receive=receive)

        with self.auto_eave_state(scope=scope) as eave_state:
            self._do_signature_verification(scope=scope, body=body, eave_state=eave_state)

        await self.app(scope, receive, send)

    @staticmethod
    def _do_signature_verification(
        scope: HTTPScope, body: bytes, eave_state: eave.stdlib.request_state.EaveRequestState
    ) -> None:
        signature = eave.stdlib.api_util.get_header_value(scope=scope, name=eave.stdlib.headers.EAVE_SIGNATURE_HEADER)
        if not signature:
            # reject None or empty strings
            raise eave.stdlib.exceptions.MissingRequiredHeaderError(eave.stdlib.headers.EAVE_SIGNATURE_HEADER)

        payload = body.decode()
        team_id_header = eave.stdlib.api_util.get_header_value(
            scope=scope, name=eave.stdlib.headers.EAVE_TEAM_ID_HEADER
        )
        account_id_header = eave.stdlib.api_util.get_header_value(
            scope=scope, name=eave.stdlib.headers.EAVE_ACCOUNT_ID_HEADER
        )

        message = eave.stdlib.requests.build_message_to_sign(
            method=scope["method"],
            url=eave.stdlib.core_api.client.makeurl(scope["path"]),
            request_id=eave.stdlib.util.unwrap(eave_state.request_id),
            origin=eave.stdlib.util.unwrap(eave_state.eave_origin),
            team_id=team_id_header,
            account_id=account_id_header,
            payload=payload,
        )

        signing_key = eave.stdlib.signing.get_key(signer=eave.stdlib.util.unwrap(eave_state.eave_origin))

        eave.stdlib.signing.verify_signature_or_exception(
            signing_key=signing_key,
            message=message,
            signature=signature,
        )
