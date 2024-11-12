from dataclasses import dataclass
from http import HTTPStatus

import starlette.exceptions

"""
Exceptions for internal GraphQL error handling. These
do not set any HTTP status codes because handled non-500 errors
get the 200 OK status in GraphQL, and have to be parsed from
the response body.
"""


@dataclass
class ValidationError(Exception):
    field: str


class StartTimeTooSoonError(Exception):
    pass


class StartTimeTooLateError(Exception):
    pass


"""
Convenience classes for raising an error with a specific error code.
Errors that inherit HTTPException are intended to be handled as HTTP errors. For example, if a resource isn't found,
an HTTPException may be raised with status code 404. In this case, no error is logged in our monitoring systems.
Most errors that do not inherit HTTPException aren't specifically handled anywhere and will show up in our error logs.
Errors like this should just be thrown, and let the middleware handle logging.
"""


class HTTPException(starlette.exceptions.HTTPException):
    request_id: str | None = None
    code: int
    """
    alias for status_code
    """

    def __init__(
        self,
        status_code: int,
        detail: str | None = None,
        headers: dict[str, str] | None = None,
        request_id: str | None = None,
    ) -> None:
        self.request_id = request_id
        self.code = status_code
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class BadRequestError(HTTPException):
    def __init__(
        self,
        detail: str | None = None,
        headers: dict[str, str] | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(status_code=HTTPStatus.BAD_REQUEST, detail=detail, headers=headers, request_id=request_id)


class UnauthorizedError(HTTPException):
    def __init__(
        self,
        detail: str | None = None,
        headers: dict[str, str] | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(status_code=HTTPStatus.UNAUTHORIZED, detail=detail, headers=headers, request_id=request_id)


class ForbiddenError(HTTPException):
    def __init__(
        self,
        detail: str | None = None,
        headers: dict[str, str] | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(status_code=HTTPStatus.FORBIDDEN, detail=detail, headers=headers, request_id=request_id)


class NotFoundError(HTTPException):
    def __init__(
        self,
        detail: str | None = None,
        headers: dict[str, str] | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(status_code=HTTPStatus.NOT_FOUND, detail=detail, headers=headers, request_id=request_id)


class LengthRequiredError(HTTPException):
    def __init__(
        self,
        detail: str | None = None,
        headers: dict[str, str] | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(status_code=HTTPStatus.LENGTH_REQUIRED, detail=detail, headers=headers, request_id=request_id)


class RequestEntityTooLargeError(HTTPException):
    def __init__(
        self,
        detail: str | None = None,
        headers: dict[str, str] | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(
            status_code=HTTPStatus.REQUEST_ENTITY_TOO_LARGE, detail=detail, headers=headers, request_id=request_id
        )


class UnprocessableEntityError(HTTPException):
    def __init__(
        self,
        detail: str | None = None,
        headers: dict[str, str] | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=detail, headers=headers, request_id=request_id
        )


class InternalServerError(HTTPException):
    def __init__(
        self,
        detail: str | None = None,
        headers: dict[str, str] | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=detail, headers=headers, request_id=request_id
        )


"""
Convenience classes
"""


class InvalidAuthError(UnauthorizedError):
    pass


class InvalidJWSError(UnauthorizedError):
    pass


class InvalidJWTError(UnauthorizedError):
    pass


class AccessTokenExpiredError(UnauthorizedError):
    pass


class InvalidSignatureError(BadRequestError):
    pass


class InvalidOriginError(BadRequestError):
    pass


class InvalidStateError(BadRequestError):
    pass


class MissingRequiredHeaderError(BadRequestError):
    pass


"""
Custom exceptions to help group exceptions in our error reporting system.
All of these will return a 500 error (the default) to the client.
"""


class MaxRetryAttemptsReachedError(Exception):
    pass


class InvalidChecksumError(Exception):
    pass


class DataConflictError(Exception):
    pass


class MissingOAuthCredentialsError(Exception):
    pass


class UnexpectedMissingValueError(Exception):
    pass


class OpenAIDataError(Exception):
    pass


class SecretRetrievalError(Exception):
    pass


class RuntimeConfigRetrievalError(Exception):
    pass
