import uuid

from eave.core.internal.orm.team import TeamOrm
from eave.stdlib.core_api.operations import EndpointConfiguration

import eave.stdlib.exceptions
import eave.stdlib.api_util
import eave.stdlib.headers
import eave.core.internal
import eave.core.public
import asgiref.typing
import starlette.types

from eave.stdlib.middleware.base import EaveASGIMiddleware
from eave.stdlib.request_state import EaveRequestState


class TeamLookupASGIMiddleware(EaveASGIMiddleware):
    endpoint_config: EndpointConfiguration

    def __init__(self, app: starlette.types.ASGIApp, endpoint_config: EndpointConfiguration) -> None:
        super().__init__(app)
        self.endpoint_config = endpoint_config

    async def run(
        self,
        scope: asgiref.typing.Scope,
        receive: asgiref.typing.ASGIReceiveCallable,
        send: asgiref.typing.ASGISendCallable,
    ) -> None:
        if scope["type"] == "http":
            await self._lookup_team(scope=scope)

        await self.app(scope, receive, send)

    async def _lookup_team(self, scope: asgiref.typing.HTTPScope) -> None:
        eave_state = EaveRequestState.load(scope=scope)

        team_id_header = eave.stdlib.api_util.get_header_value(
            scope=scope, name=eave.stdlib.headers.EAVE_TEAM_ID_HEADER
        )

        if not team_id_header:
            if not self.endpoint_config.team_id_required:
                return
            else:
                raise eave.stdlib.exceptions.MissingRequiredHeaderError(eave.stdlib.headers.EAVE_TEAM_ID_HEADER)

        team_id = uuid.UUID(team_id_header)  # throws ValueError for invalid UUIDs
        async with eave.core.internal.database.async_session.begin() as db_session:
            team = await TeamOrm.one_or_none(session=db_session, team_id=team_id)
            if not team:
                raise eave.stdlib.exceptions.NotFoundError("invalid team ID")

            eave_state.ctx.eave_team_id = str(team.id)
