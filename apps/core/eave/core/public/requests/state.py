from dataclasses import dataclass
from typing import Optional
import uuid
import starlette.datastructures
import eave.core.internal.orm as eave_orm
import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.jwt as eave_jwt

class EaveRequestState:
    """
    Wrapper around Starlette Request State object, to give type hinting.
    """
    def __init__(self, state: starlette.datastructures.State) -> None:
        self._state = state

    @property
    def eave_account(self) -> eave_orm.AccountOrm:
        value: eave_orm.AccountOrm = self._state.eave_account
        return value

    @property
    def eave_origin(self) -> eave_origins.EaveOrigin:
        value: eave_origins.EaveOrigin = self._state.eave_origin
        return value

    @property
    def eave_team(self) -> eave_orm.TeamOrm:
        value: eave_orm.TeamOrm = self._state.eave_team
        return value

    @property
    def request_id(self) -> uuid.UUID:
        value: uuid.UUID = self._state.request_id
        return value
