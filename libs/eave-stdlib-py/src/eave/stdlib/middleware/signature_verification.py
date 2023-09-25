from asgiref.typing import ASGI3Application, ASGIReceiveCallable, ASGISendCallable, HTTPScope, Scope

from eave.stdlib.eave_origins import EaveApp

from .base import EaveASGIMiddleware
from .development_bypass import development_bypass_allowed
from ..logging import eaveLogger
from ..api_util import get_header_value
from ..headers import EAVE_SIG_TS_HEADER, EAVE_SIGNATURE_HEADER, EAVE_TEAM_ID_HEADER, EAVE_ACCOUNT_ID_HEADER
from ..exceptions import InvalidSignatureError, MissingRequiredHeaderError
from ..request_state import EaveRequestState
from ..util import unwrap
from .. import signing

MAX_SIGNATURE_AGE = 60 * 60  # 1h


class SignatureVerificationASGIMiddleware(EaveASGIMiddleware):
    """
    Reads the body and headers and verifies the signature.
    Note that this middleware necessarily blocks the request until the full body is received,
    so that it can calculate the expected signature and compare it to the provided signature.
    """

    audience: EaveApp

    def __init__(self, app: ASGI3Application, audience: EaveApp):
        super().__init__(app)
        self.audience = audience

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

    def _do_signature_verification(self, scope: HTTPScope, body: bytes) -> None:
        eave_state = EaveRequestState.load(scope=scope)

        signature = get_header_value(scope=scope, name=EAVE_SIGNATURE_HEADER)
        if not signature:
            # reject None or empty strings
            raise MissingRequiredHeaderError(EAVE_SIGNATURE_HEADER)

        eave_sig_ts_header = get_header_value(scope=scope, name=EAVE_SIG_TS_HEADER)
        if not eave_sig_ts_header:
            raise MissingRequiredHeaderError(EAVE_SIG_TS_HEADER)

        eave_sig_ts = int(eave_sig_ts_header)
        now = signing.make_sig_ts()
        if now - eave_sig_ts > MAX_SIGNATURE_AGE:
            raise InvalidSignatureError("expired")

        payload = body.decode()
        team_id_header = get_header_value(scope=scope, name=EAVE_TEAM_ID_HEADER)
        account_id_header = get_header_value(scope=scope, name=EAVE_ACCOUNT_ID_HEADER)

        message = signing.build_message_to_sign(
            method=scope["method"],
            path=scope["path"],
            request_id=eave_state.ctx.eave_request_id,
            origin=unwrap(eave_state.ctx.eave_origin),
            audience=self.audience,
            ts=eave_sig_ts,
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
