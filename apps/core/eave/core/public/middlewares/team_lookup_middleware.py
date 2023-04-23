from http import HTTPStatus
import re
from typing import Any, Awaitable, Callable, List, Set
import uuid
import fastapi
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy.exc
from starlette.middleware.base import BaseHTTPMiddleware
import eave.core.public.requests.util as request_util
import eave.core.internal.orm as eave_orm
import eave.core.internal.database as eave_db
import eave.stdlib.signing as eave_signing
import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.jwt as eave_jwt
import eave.stdlib.core_api.headers as eave_headers
from . import EaveMiddleware
from eave.stdlib import logger

_BYPASS: Set[str] = set()

def add_bypass(path: str) -> None:
    global _BYPASS
    _BYPASS.add(path)

class TeamLookupMiddleware(EaveMiddleware):
    async def dispatch(self, request: fastapi.Request, call_next: Callable[[fastapi.Request], Awaitable[fastapi.Response]]) -> fastapi.Response:
        global _BYPASS
        if request.url.path not in _BYPASS:
            team_id_header = request.headers.get(eave_headers.EAVE_TEAM_ID_HEADER)
            if not team_id_header:
                logger.error("team ID header missing/empty", extra=request_util.log_context(request))
                raise fastapi.HTTPException(HTTPStatus.BAD_REQUEST)

            try:
                team_id = uuid.UUID(team_id_header)  # throws ValueError for invalid UUIDs
                async with eave_db.get_async_session() as db_session:
                    team = await eave_orm.TeamOrm.one_or_exception(session=db_session, team_id=team_id)
                    request.state.eave_team = team

            except ValueError as error:
                logger.error("invalid team ID", extra=request_util.log_context(request))
                raise fastapi.HTTPException(HTTPStatus.BAD_REQUEST) from error

            except sqlalchemy.exc.SQLAlchemyError as error:
                logger.error("team lookup failed", extra=request_util.log_context(request))
                raise fastapi.HTTPException(HTTPStatus.BAD_REQUEST) from error

        response = await call_next(request)
        return response
