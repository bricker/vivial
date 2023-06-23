from asgiref.typing import ASGI3Application, ASGIReceiveCallable, ASGISendCallable, Scope, HTTPScope

from eave.stdlib.request_state import EaveRequestState


class EaveASGIMiddleware:
    """
    https://asgi.readthedocs.io/en/latest/specs/www.html#http
    """

    app: ASGI3Application

    def __init__(self, app: ASGI3Application) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        ...

    @staticmethod
    async def read_body(scope: HTTPScope, receive: ASGIReceiveCallable) -> bytes:
        eave_state = EaveRequestState.load(scope=scope)
        if not eave_state.raw_request_body:
            body: bytes = b""

            while True:
                # https://asgi.readthedocs.io/en/latest/specs/www.html#request-receive-event
                message = await receive()
                assert message["type"] == "http.request"
                chunk: bytes = message.get("body", b"")
                body += chunk

                if message.get("more_body", False) is False:
                    break

            eave_state.raw_request_body = body

        return eave_state.raw_request_body
