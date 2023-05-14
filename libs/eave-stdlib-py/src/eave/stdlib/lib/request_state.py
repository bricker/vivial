import asyncio
import typing
import uuid
from typing import Any, Optional, cast

import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.util as eave_util
import starlette.applications
import starlette.requests
from asgiref.typing import Scope
from eave.stdlib.typing import LogContext


class EaveRequestState:
    eave_account_id: uuid.UUID
    eave_origin: eave_origins.EaveOrigin
    eave_team_id: uuid.UUID
    request_id: uuid.UUID
    request_method: str
    request_scheme: str
    request_path: str
    _notes: typing.Optional[typing.List[str]] = None

    @property
    def log_context(self) -> LogContext:
        context: dict[str, str] = dict()

        if hasattr(self, "eave_account"):
            context["eave_account_id"] = str(self.eave_account_id)
        if hasattr(self, "eave_origin"):
            context["eave_origin"] = self.eave_origin.value
        if hasattr(self, "eave_team"):
            context["eave_team_id"] = str(self.eave_team_id)
        if hasattr(self, "request_id"):
            context["request_id"] = str(self.request_id)
        if hasattr(self, "request_method"):
            context["request_method"] = str(self.request_method)
        if hasattr(self, "request_scheme"):
            context["request_scheme"] = str(self.request_scheme)
        if hasattr(self, "request_path"):
            context["request_path"] = str(self.request_path)
        # if hasattr(self, "_notes"):
        #     # Probably not thread-safe
        #     context["notes"] = self._notes

        # This response structure is for Google Cloud Logging
        return {"json_fields": context}

    @property
    def public_request_context(self) -> dict[str, str]:
        """
        Return this from an endpoint to give the caller some context.
        This is similar to log_context, except it is intended for public, and therefore shouldn't contain any
        internal information.
        """

        context: dict[str, str] = {}

        if hasattr(self, "eave_account"):
            context["eave_account_id"] = str(self.eave_account_id)
        if hasattr(self, "eave_origin"):
            context["eave_origin"] = self.eave_origin.value
        if hasattr(self, "eave_team"):
            context["eave_team_id"] = str(self.eave_team_id)
        if hasattr(self, "request_id"):
            context["request_id"] = str(self.request_id)
        if hasattr(self, "request_method"):
            context["request_method"] = str(self.request_method)
        if hasattr(self, "request_scheme"):
            context["request_scheme"] = str(self.request_scheme)
        if hasattr(self, "request_path"):
            context["request_path"] = str(self.request_path)

        return context

    _semaphore = asyncio.Semaphore()

    async def add_note(self, note: str) -> None:
        async with self._semaphore:
            if self._notes is None:
                self._notes = []

            self._notes.append(note)


def get_eave_state(
    scope: Optional[Scope] = None, request: Optional[starlette.requests.Request] = None
) -> EaveRequestState:
    # Validate that exactly one parameter is supplied.
    assert eave_util.xor(scope, request)

    if scope is None and request is not None:
        scope = cast(Scope, request.scope)

    assert scope is not None
    scope.setdefault("state", dict[str, Any]())
    state = scope.get("state")
    assert state is not None  # Helps the typechecker

    eave_state = state.get("eave")
    if eave_state is None:
        eave_state = EaveRequestState()
        state["eave"] = eave_state

    if scope["type"] == "http":
        eave_state.request_method = scope["method"]
        eave_state.request_scheme = scope["scheme"]
        eave_state.request_path = scope["path"]

    return cast(EaveRequestState, eave_state)
