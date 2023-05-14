import uuid

import eave.stdlib.exceptions as eave_errors
import eave.stdlib.headers as eave_headers
import sqlalchemy.exc
from asgiref.typing import ASGIReceiveCallable, ASGISendCallable, HTTPScope, Scope
from eave.stdlib import api_util, logger

import eave.core.internal.database as eave_db
import eave.stdlib.lib.request_state as request_util
from eave.core.internal.orm.team import TeamOrm

from . import EaveASGIMiddleware


class TeamLookupASGIMiddleware(EaveASGIMiddleware):
    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        if scope["type"] == "http":
            await self._lookup_team(scope=scope)

        await self.app(scope, receive, send)

    @staticmethod
    async def _lookup_team(scope: HTTPScope) -> None:
        eave_state = request_util.get_eave_state(scope=scope)
        team_id_header = api_util.get_header_value(scope=scope, name=eave_headers.EAVE_TEAM_ID_HEADER)

        try:
            if hasattr(eave_state, "eave_team"):
                # If eave_team was already set in another middleware (eg, in auth_middleware),
                # then make sure it's the same team and move on.
                team_id = uuid.UUID(team_id_header)
                if eave_state.eave_team.id == team_id:
                    return
                else:
                    logger.error("team ID header does not match account", extra=eave_state.log_context)
                    raise eave_errors.BadRequestError()

            if not team_id_header:
                logger.error("team ID header missing/empty", extra=eave_state.log_context)
                raise eave_errors.MissingRequiredHeaderError("eave-team-id")

            team_id = uuid.UUID(team_id_header)  # throws ValueError for invalid UUIDs
            async with eave_db.async_session.begin() as db_session:
                team = await TeamOrm.one_or_exception(session=db_session, team_id=team_id)
                eave_state.eave_team = team

        except ValueError as e:
            logger.error("invalid team ID", exc_info=e, extra=eave_state.log_context)
            raise eave_errors.BadRequestError() from e

        except sqlalchemy.exc.SQLAlchemyError as e:
            logger.error("team lookup failed", exc_info=e, extra=eave_state.log_context)
            raise eave_errors.BadRequestError() from e
