from typing import Any, Generic, Optional, TypeVar, cast
from uuid import UUID

from starlette.datastructures import State

JsonObject = dict[str, Any]

# JsonScalar = str | int | bool
# JsonObject = dict[str, "AnyJsonType"]
# JsonArray = list["AnyJsonType"]
# AnyJsonType = JsonObject | JsonArray | JsonScalar


class StateWrapper:
    """
    Wraps starlette State object (effectively a dict) to add concrete properties.
    """

    _state: State

    def __init__(self, state: State) -> None:
        self._state = state

    @property
    def team_id(self) -> Optional[UUID]:
        try:
            value = cast(UUID, self._state.team_id)
            return value
        except AttributeError:
            return None
