from dataclasses import dataclass
from typing import Optional
import starlette.datastructures


class EaveRequestState:
    """
    Wrapper around Starlette Request State object, to give type hinting.
    """
    def __init__(self, state: starlette.datastructures.State) -> None:
        self._state = state

    @property
    def eave_auth_token(self) -> str:
        value: str = self._state.eave_auth_token
        return value

    @property
    def eave_team_id(self) -> Optional[str]:
        value: str = self._state.eave_team_id
        return value
