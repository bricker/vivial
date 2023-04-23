import logging
from http import HTTPStatus
from http.client import HTTPException
from typing import Any
from uuid import UUID

import eave.core.internal.orm as eave_orm
import eave.stdlib.exceptions as eave_errors
import fastapi
import sqlalchemy.exc
from eave.stdlib import logger
from sqlalchemy.ext.asyncio import AsyncSession

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


def add_standard_exception_handlers(app: fastapi.FastAPI) -> None:
    app.exception_handler(sqlalchemy.exc.NoResultFound)(not_found)
    app.exception_handler(sqlalchemy.exc.MultipleResultsFound)(internal_server_error)
    app.exception_handler(eave_errors.BadRequestError)(bad_request)
    app.exception_handler(eave_errors.UnauthorizedError)(unauthorized)
    app.exception_handler(eave_errors.InternalServerError)(internal_server_error)
    app.exception_handler(fastapi.exceptions.RequestValidationError)(validation_error)

def log_context(request: fastapi.Request) -> dict[str, Any]:
    context = {
        "request_id": request.state.request_id,
    }
    return context