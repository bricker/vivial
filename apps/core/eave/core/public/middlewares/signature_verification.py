import eave.stdlib
import eave.core.public
from asgiref.typing import ASGIReceiveCallable, ASGIReceiveEvent, ASGISendCallable, HTTPScope, Scope

from . import EaveASGIMiddleware, development_bypass


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
            eave.stdlib.logger.warning("Bypassing signature verification in dev environment")
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

        with self.auto_eave_state(scope=scope) as eave_state:
            self._do_signature_verification(scope=scope, body=body, eave_state=eave_state)

        async def dummy_receive() -> ASGIReceiveEvent:
            return {
                "type": "http.request",
                "body": body,
                "more_body": False,
            }

        await self.app(scope, dummy_receive, send)

    @staticmethod
    def _do_signature_verification(
        scope: HTTPScope, body: bytes, eave_state: eave.core.public.request_state.EaveRequestState
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

        message = eave.stdlib.core_api.client.build_message_to_sign(
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
