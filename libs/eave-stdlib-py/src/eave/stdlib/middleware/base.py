from contextlib import contextmanager
from typing import Any, Generator
from asgiref.typing import ASGI3Application, ASGIReceiveCallable, ASGISendCallable, Scope, HTTPScope
from ..request_state import EaveRequestState, set_eave_state, get_eave_state

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
    @contextmanager
    def auto_eave_state(scope: HTTPScope) -> Generator[EaveRequestState, Any, None]:
        eave_state = EaveASGIMiddleware.eave_state(scope=scope)
        yield eave_state
        set_eave_state(scope=scope, eave_state=eave_state)

    @staticmethod
    def eave_state(scope: HTTPScope) -> EaveRequestState:
        return get_eave_state(scope=scope)

    @staticmethod
    async def read_body(scope: HTTPScope, receive: ASGIReceiveCallable) -> bytes:
        with EaveASGIMiddleware.auto_eave_state(scope=scope) as eave_state:
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
