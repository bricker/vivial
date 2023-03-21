from http import HTTPStatus
from http.client import HTTPException
from uuid import UUID
import fastapi
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy.exc
from eave_core.internal.config import app_config
import eave_core.internal.orm as eave_orm
import eave_stdlib.util as eave_util
import eave_stdlib.core_api.signing as eave_signing

async def get_team_or_fail(session: AsyncSession, request: fastapi.Request) -> eave_orm.TeamOrm:
    try:
        team_id_str = request.headers.get('eave-team-id')
        if not team_id_str: # reject None or empty string
            raise ValueError()

        team_id = UUID(team_id_str) # throws ValueError for invalid UUIDs
        team = await eave_orm.TeamOrm.one_or_exception(session=session, team_id=team_id)
        return team

    except ValueError as error: # UUID parsing error
        raise HTTPException(HTTPStatus.BAD_REQUEST) from error

    except sqlalchemy.exc.SQLAlchemyError as error:
        raise HTTPException(HTTPStatus.UNAUTHORIZED) from error

def not_found() -> fastapi.Response:
    return fastapi.responses.Response(status_code=HTTPStatus.NOT_FOUND)

def internal_server_error() -> fastapi.Response:
    return fastapi.responses.Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

def bad_request() -> fastapi.Response:
    return fastapi.responses.Response(status_code=HTTPStatus.BAD_REQUEST)

def add_standard_exception_handlers(app: fastapi.FastAPI) -> None:
    app.exception_handler(sqlalchemy.exc.NoResultFound)(not_found)
    app.exception_handler(sqlalchemy.exc.MultipleResultsFound)(internal_server_error)
    app.exception_handler(eave_signing.InvalidSignatureError)(bad_request)
