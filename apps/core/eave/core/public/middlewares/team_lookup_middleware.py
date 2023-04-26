import uuid
from http import HTTPStatus
from typing import Set

import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.core.public.requests.util as request_util
import eave.stdlib.core_api.headers as eave_headers
import eave.stdlib.exceptions as eave_errors
import fastapi
import sqlalchemy.exc
from eave.stdlib import logger

from . import EaveASGIMiddleware, asgi_types

_BYPASS: Set[str] = set()


def add_bypass(path: str) -> None:
    global _BYPASS
    _BYPASS.add(path)


class TeamLookupASGIMiddleware(EaveASGIMiddleware):
    async def __call__(
        self, scope: asgi_types.Scope, receive: asgi_types.ASGIReceiveCallable, send: asgi_types.ASGISendCallable
    ) -> None:
        if scope["type"] == "http" and scope["path"] not in _BYPASS:
            await self._lookup_team(scope=scope)

        await self.app(scope, receive, send)

    @staticmethod
    async def _lookup_team(scope: asgi_types.HTTPScope) -> None:
        team_id_header = request_util.get_header_value(scope=scope, name=eave_headers.EAVE_TEAM_ID_HEADER)
        if not team_id_header:
            logger.error("team ID header missing/empty", extra=request_util.log_context(scope=scope))
            raise eave_errors.MissingRequiredHeaderError("eave-team-id")

        try:
            team_id = uuid.UUID(team_id_header)  # throws ValueError for invalid UUIDs
            async with eave_db.get_async_session() as db_session:
                team = await eave_orm.TeamOrm.one_or_exception(session=db_session, team_id=team_id)
                request_util.get_eave_state(scope=scope).eave_team = team

        except ValueError as error:
            logger.error("invalid team ID", extra=request_util.log_context(scope=scope))
            raise eave_errors.BadRequestError() from error

        except sqlalchemy.exc.SQLAlchemyError as error:
            logger.error("team lookup failed", extra=request_util.log_context(scope=scope))
            raise eave_errors.BadRequestError() from error
