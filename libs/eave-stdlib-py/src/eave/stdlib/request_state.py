import logging
from typing import Optional, cast

import eave.stdlib
import starlette.applications
import starlette.requests
from asgiref.typing import HTTPScope
import eave.stdlib.logging

from eave.stdlib.typing import JsonObject

SCOPE_KEY = "eave_state"


class EaveRequestState:
    eave_account_id: Optional[str] = None
    eave_team_id: Optional[str] = None
    eave_origin: Optional[str] = None
    eave_request_id: Optional[str] = None
    request_method: Optional[str] = None
    request_scheme: Optional[str] = None
    request_path: Optional[str] = None
    request_headers: Optional[dict[str, str]] = None
    raw_request_body: Optional[bytes] = None
    parsed_request_body: Optional[JsonObject] = None

    def __init__(self, attrs: dict[object, object]) -> None:
        for key, _ in self.__annotations__.items():
            if v := attrs.get(key):
                self.__setattr__(key, v)

    @property
    def log_context(self) -> eave.stdlib.logging.LogContext:
        payload = {
            "eave_account_id": str(self.eave_account_id),
            "eave_team_id": str(self.eave_team_id),
            "eave_origin": str(self.eave_origin),
            "eave_request_id": str(self.eave_request_id),
            "request_method": str(self.request_method),
            "request_scheme": str(self.request_scheme),
            "request_path": str(self.request_path),
            "request_headers": self.request_headers,
        }

        if eave.stdlib.logging.eaveLogger.level == logging.DEBUG:
            payload["request_body"] = self.parsed_request_body

        return eave.stdlib.logging.LogContext().set(payload)

    @property
    def public_request_context(self) -> eave.stdlib.typing.JsonObject:
        """
        Return this from an endpoint to give the caller some context.
        This is similar to log_context, except it is intended for public, and therefore shouldn't contain any
        internal information.
        """

        payload = {
            "eave_request_id": str(self.eave_request_id),
        }
        return payload


def get_eave_state(
    scope: Optional[HTTPScope] = None, request: Optional[starlette.requests.Request] = None
) -> EaveRequestState:
    normalized_scope = _normalized_scope(scope=scope, request=request)
    eave_state_serialized = _eave_state_serialized(scope=normalized_scope)
    eave_state = EaveRequestState(attrs=eave_state_serialized)
    return eave_state


def set_eave_state(
    eave_state: EaveRequestState,
    scope: Optional[HTTPScope] = None,
    request: Optional[starlette.requests.Request] = None,
) -> None:
    normalized_scope = _normalized_scope(scope=scope, request=request)
    assert normalized_scope["extensions"] is not None, "typecheck only"
    odict = cast(dict[object, object], eave_state.__dict__)
    normalized_scope["extensions"][SCOPE_KEY] = odict


def _eave_state_serialized(scope: HTTPScope) -> dict[object, object]:
    assert scope["extensions"] is not None, "typecheck only"
    return scope["extensions"].setdefault(SCOPE_KEY, {})


def _normalized_scope(
    scope: Optional[HTTPScope] = None, request: Optional[starlette.requests.Request] = None
) -> HTTPScope:
    # Validate that exactly one parameter is supplied.
    assert eave.stdlib.util.xor(scope, request), "invalid parameters"

    if scope is None and request is not None:
        scope = cast(HTTPScope, request.scope)

    assert scope is not None, "typecheck only"

    if "extensions" not in scope or scope["extensions"] is None:
        scope["extensions"] = {}

    return scope
