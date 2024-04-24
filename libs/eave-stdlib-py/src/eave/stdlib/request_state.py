from typing import cast

import starlette.applications
import starlette.requests
from asgiref.typing import HTTPScope

from .logging import LogContext
from .util import xor

SCOPE_KEY = "eave_state"


class EaveRequestState(dict[object, object]):
    raw_request_body: bytes | None = None
    ctx: LogContext

    @classmethod
    def load(
        cls, scope: HTTPScope | None = None, request: starlette.requests.Request | None = None
    ) -> "EaveRequestState":
        # Validate that exactly one parameter is supplied.
        assert xor(scope, request), "invalid parameters"

        if scope is None and request is not None:
            scope = cast(HTTPScope, request.scope)

        assert scope is not None, "typecheck only"

        if "extensions" not in scope or scope["extensions"] is None:
            scope["extensions"] = {}

        assert scope["extensions"] is not None, "typecheck only"
        eave_state = scope["extensions"].setdefault(SCOPE_KEY, EaveRequestState(scope=scope))
        return cast(EaveRequestState, eave_state)

    def __init__(self, scope: HTTPScope | None) -> None:
        self.ctx = LogContext(scope=scope)
