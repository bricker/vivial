import logging
from http import HTTPStatus
from http.client import HTTPException
from uuid import UUID

import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.signing as eave_signing
import fastapi
import sqlalchemy.exc
from eave.stdlib import logger
from sqlalchemy.ext.asyncio import AsyncSession


async def get_team_or_fail(session: AsyncSession, request: fastapi.Request) -> eave_orm.TeamOrm:
    try:
        team_id_str = request.headers.get("eave-team-id")
        if not team_id_str:  # reject None or empty string
            raise ValueError()

        team_id = UUID(team_id_str)  # throws ValueError for invalid UUIDs
        team = await eave_orm.TeamOrm.one_or_exception(session=session, team_id=team_id)
        return team

    except ValueError as error:  # UUID parsing error
        raise HTTPException(HTTPStatus.BAD_REQUEST) from error

    except sqlalchemy.exc.SQLAlchemyError as error:
        raise HTTPException(HTTPStatus.BAD_REQUEST) from error


async def validate_signature_or_fail(request: fastapi.Request) -> None:
    body = await request.body()
    payload = body.decode()
    actual_signature = request.headers.get(eave_signing.SIGNATURE_HEADER_NAME)
    team_id = request.headers.get(eave_signing.TEAM_ID_HEADER_NAME)

    if not actual_signature or not payload:
        # reject None or empty strings
        raise eave_signing.InvalidSignatureError()

    expected_signature = eave_signing.sign(payload=payload, team_id=team_id)
    if not eave_signing.compare_signatures(expected=expected_signature, actual=actual_signature):
        raise eave_signing.InvalidSignatureError()


def not_found(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    logging.error("not found", exc_info=exc)
    return fastapi.responses.Response(status_code=HTTPStatus.NOT_FOUND)


def internal_server_error(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    logging.error("internal server error", exc_info=exc)
    return fastapi.responses.Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


def bad_request(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    logging.error("bad request", exc_info=exc)
    return fastapi.responses.Response(status_code=HTTPStatus.BAD_REQUEST)


def validation_error(request: fastapi.Request, exc: fastapi.exceptions.RequestValidationError) -> fastapi.Response:
    logger.error(exc)
    logger.info(exc.body)
    return fastapi.Response(status_code=HTTPStatus.UNPROCESSABLE_ENTITY)


def add_standard_exception_handlers(app: fastapi.FastAPI) -> None:
    app.exception_handler(sqlalchemy.exc.NoResultFound)(not_found)
    app.exception_handler(sqlalchemy.exc.MultipleResultsFound)(internal_server_error)
    app.exception_handler(eave_signing.InvalidSignatureError)(bad_request)
    app.exception_handler(fastapi.exceptions.RequestValidationError)(validation_error)
