from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, HTTPScope, Scope

from .base import EaveASGIMiddleware
from .development_bypass import development_bypass_allowed
from ..logging import eaveLogger
from ..api_util import construct_url, get_header_value
from ..headers import EAVE_SIGNATURE_HEADER, EAVE_TEAM_ID_HEADER, EAVE_ACCOUNT_ID_HEADER, HOST
from ..exceptions import MissingRequiredHeaderError
from ..request_state import EaveRequestState
from ..util import unwrap
from .. import signing


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

        if development_bypass_allowed(scope=scope):
            eaveLogger.warning("Bypassing signature verification in dev environment")
            await self.app(scope, receive, send)
            return

        body = await self.read_body(scope=scope, receive=receive)
        self._do_signature_verification(scope=scope, body=body)

        await self.app(scope, receive, send)

    @staticmethod
    def _do_signature_verification(scope: HTTPScope, body: bytes) -> None:
        eave_state = EaveRequestState.load(scope=scope)

        signature = get_header_value(scope=scope, name=EAVE_SIGNATURE_HEADER)
        if not signature:
            # reject None or empty strings
            raise MissingRequiredHeaderError(EAVE_SIGNATURE_HEADER)

        payload = body.decode()
        team_id_header = get_header_value(scope=scope, name=EAVE_TEAM_ID_HEADER)
        account_id_header = get_header_value(scope=scope, name=EAVE_ACCOUNT_ID_HEADER)

        message = signing.build_message_to_sign(
            method=scope["method"],
            url=construct_url(scope=scope),
            request_id=eave_state.ctx.eave_request_id,
            origin=unwrap(eave_state.ctx.eave_origin),
            team_id=team_id_header,
            account_id=account_id_header,
            payload=payload,
            ctx=eave_state.ctx,
        )

        signing_key = signing.get_key(signer=unwrap(eave_state.ctx.eave_origin))

        signing.verify_signature_or_exception(
            signing_key=signing_key,
            message=message,
            signature=signature,
        )
