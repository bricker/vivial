import uuid
from typing import Set

import eave.core.internal.database as eave_db
import eave.core.public.requests.util as request_util
import eave.stdlib.exceptions as eave_errors
import eave.stdlib.headers as eave_headers
import sqlalchemy.exc
from eave.core.internal.orm.team import TeamOrm
from eave.stdlib import logger

from . import EaveASGIMiddleware, asgi_types

_ROUTE_BYPASS: Set[str] = set()


def add_bypass(path: str) -> None:
    global _ROUTE_BYPASS
    _ROUTE_BYPASS.add(path)


class TeamLookupASGIMiddleware(EaveASGIMiddleware):
    async def __call__(
        self, scope: asgi_types.Scope, receive: asgi_types.ASGIReceiveCallable, send: asgi_types.ASGISendCallable
    ) -> None:
        if scope["type"] == "http" and scope["path"] not in _ROUTE_BYPASS:
            await self._lookup_team(scope=scope)

        await self.app(scope, receive, send)

    @staticmethod
    async def _lookup_team(scope: asgi_types.HTTPScope) -> None:
        eave_state = request_util.get_eave_state(scope=scope)
        team_id_header = request_util.get_header_value(scope=scope, name=eave_headers.EAVE_TEAM_ID_HEADER)
        if not team_id_header:
            logger.error("team ID header missing/empty", extra=eave_state.log_context)
            raise eave_errors.MissingRequiredHeaderError("eave-team-id")

        try:
            team_id = uuid.UUID(team_id_header)  # throws ValueError for invalid UUIDs
            async with eave_db.async_session.begin() as db_session:
                team = await TeamOrm.one_or_exception(session=db_session, team_id=team_id)
                request_util.get_eave_state(scope=scope).eave_team = team

        except ValueError as e:
            logger.error("invalid team ID", exc_info=e, extra=eave_state.log_context)
            raise eave_errors.BadRequestError() from e

        except sqlalchemy.exc.SQLAlchemyError as e:
            logger.error("team lookup failed", exc_info=e, extra=eave_state.log_context)
            raise eave_errors.BadRequestError() from e
