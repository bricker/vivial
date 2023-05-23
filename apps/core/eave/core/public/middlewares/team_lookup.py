import uuid

import eave.stdlib
import eave.core.internal
import eave.core.public
from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, HTTPScope, Scope

from eave.stdlib.middleware.base import EaveASGIMiddleware
from eave.stdlib.request_state import EaveRequestState


class TeamLookupASGIMiddleware(EaveASGIMiddleware):
    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if scope["type"] == "http":
            with self.auto_eave_state(scope=scope) as eave_state:
                await self._lookup_team(scope=scope, eave_state=eave_state)

        await self.app(scope, receive, send)

    @staticmethod
    async def _lookup_team(scope: HTTPScope, eave_state: EaveRequestState) -> None:
        team_id_header = eave.stdlib.api_util.get_header_value(
            scope=scope, name=eave.stdlib.headers.EAVE_TEAM_ID_HEADER
        )

        if eave_state.eave_team_id:
            # If eave_team was already set in another middleware (eg, in auth_middleware),
            # then make sure it's the same team and move on.
            team_id = uuid.UUID(team_id_header)
            if eave_state.eave_team_id == team_id:
                return
            else:
                raise eave.stdlib.exceptions.BadRequestError("mismatched team and account")

        if not team_id_header:
            raise eave.stdlib.exceptions.MissingRequiredHeaderError(eave.stdlib.headers.EAVE_TEAM_ID_HEADER)

        team_id = uuid.UUID(team_id_header)  # throws ValueError for invalid UUIDs
        async with eave.core.internal.database.async_session.begin() as db_session:
            team = await eave.core.internal.orm.TeamOrm.one_or_exception(session=db_session, team_id=team_id)
            eave_state.eave_team_id = str(team.id)
