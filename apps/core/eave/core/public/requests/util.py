import logging
from http import HTTPStatus
from http.client import HTTPException
import re
from uuid import UUID

import eave.core.internal.orm as eave_orm
import eave.stdlib.signing as eave_signing
import eave.stdlib.jwt as eave_jwt
import eave.stdlib.eave_origins as eave_origins
import fastapi
import sqlalchemy.exc
from eave.stdlib import logger
from sqlalchemy.ext.asyncio import AsyncSession

EAVE_SIGNATURE_HEADER = "eave-signature"
EAVE_TEAM_ID_HEADER = "eave-team-id"
EAVE_ORIGIN_HEADER = "eave-origin"
AUTHORIZATION_HEADER = "authorization"

async def get_team_or_fail(session: AsyncSession, request: fastapi.Request) -> eave_orm.TeamOrm:
    try:
        team_id_str = request.headers.get(EAVE_TEAM_ID_HEADER)
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
    signature = request.headers.get(EAVE_SIGNATURE_HEADER)

    if not signature or not payload:
        # reject None or empty strings
        raise eave_signing.InvalidSignatureError()

    origin_header = request.headers.get(EAVE_ORIGIN_HEADER)
    assert origin_header is not None
    origin = eave_origins.EaveOrigin(value=origin_header)

    signing_key = eave_signing.get_key(signer=origin.value)
    eave_signing.validate_signature_or_exception(
        signing_key=signing_key,
        message=payload,
        signature=signature,
    )

async def validate_auth_token_or_fail(request: fastapi.Request) -> str:
    auth_header = request.headers.get(AUTHORIZATION_HEADER)
    if not auth_header:
        raise InvalidAuthError()

    auth_header_match = re.match("^bearer (.+)$", auth_header, re.IGNORECASE)
    if auth_header_match is None:
        raise InvalidAuthError()

    auth_token = auth_header_match.group(1)
    signing_key = eave_signing.get_key(eave_origins.EaveOrigin.eave_api.value)
    eave_jwt.validate_jwt_or_exception(
        jwt_encoded=auth_token,
        signing_key=signing_key,
    )

    return auth_token

def not_found(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    logging.error("not found", exc_info=exc)
    return fastapi.responses.Response(status_code=HTTPStatus.NOT_FOUND)


def internal_server_error(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    logging.error("internal server error", exc_info=exc)
    return fastapi.responses.Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


def bad_request(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    logging.error("bad request", exc_info=exc)
    return fastapi.responses.Response(status_code=HTTPStatus.BAD_REQUEST)

def unauthorized(request: fastapi.Request, exc: Exception) -> fastapi.Response:
    logging.error("unauthorized", exc_info=exc)
    return fastapi.responses.Response(status_code=HTTPStatus.UNAUTHORIZED)


def validation_error(request: fastapi.Request, exc: fastapi.exceptions.RequestValidationError) -> fastapi.Response:
    logger.error(exc)
    logger.info(exc.body)
    return fastapi.Response(status_code=HTTPStatus.UNPROCESSABLE_ENTITY)


class InvalidAuthError(Exception):
    pass

def add_standard_exception_handlers(app: fastapi.FastAPI) -> None:
    app.exception_handler(sqlalchemy.exc.NoResultFound)(not_found)
    app.exception_handler(sqlalchemy.exc.MultipleResultsFound)(internal_server_error)
    app.exception_handler(eave_signing.InvalidSignatureError)(bad_request)
    app.exception_handler(InvalidAuthError)(unauthorized)
    app.exception_handler(fastapi.exceptions.RequestValidationError)(validation_error)
