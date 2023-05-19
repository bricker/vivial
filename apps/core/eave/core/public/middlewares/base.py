from contextlib import contextmanager
from typing import Any, Generator
import eave.core.public
from asgiref.typing import ASGI3Application, ASGIReceiveCallable, ASGISendCallable, Scope, HTTPScope


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
    def auto_eave_state(scope: HTTPScope) -> Generator[eave.core.public.request_state.EaveRequestState, Any, None]:
        eave_state = EaveASGIMiddleware.eave_state(scope=scope)
        yield eave_state
        eave.core.public.request_state.set_eave_state(scope=scope, eave_state=eave_state)

    @staticmethod
    def eave_state(scope: HTTPScope) -> eave.core.public.request_state.EaveRequestState:
        return eave.core.public.request_state.get_eave_state(scope=scope)
