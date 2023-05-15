from http import HTTPStatus
import typing
from starlette.exceptions import HTTPException

"""
Convenience classes for raising an error with a specific error code.
Errors that inherit HTTPException are intended to be handled as HTTP errors. For example, if a resource isn't found,
an HTTPException may be raised with status code 404. In this case, no error is logged in our monitoring systems.
Most errors that do not inherit HTTPException aren't specifically handled anywhere and will show up in our error logs.
Errors like this should just be thrown, and let the middleware handle logging.
"""


class BadRequestError(HTTPException):
    def __init__(self, detail: typing.Optional[str] = None, headers: typing.Optional[dict[str, str]] = None) -> None:
        super().__init__(status_code=HTTPStatus.BAD_REQUEST, detail=detail, headers=headers)


class UnauthorizedError(HTTPException):
    def __init__(self, detail: typing.Optional[str] = None, headers: typing.Optional[dict[str, str]] = None) -> None:
        super().__init__(status_code=HTTPStatus.UNAUTHORIZED, detail=detail, headers=headers)


class NotFoundError(HTTPException):
    def __init__(self, detail: typing.Optional[str] = None, headers: typing.Optional[dict[str, str]] = None) -> None:
        super().__init__(status_code=HTTPStatus.NOT_FOUND, detail=detail, headers=headers)


class InternalServerError(HTTPException):
    def __init__(self, detail: typing.Optional[str] = None, headers: typing.Optional[dict[str, str]] = None) -> None:
        super().__init__(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=detail, headers=headers)


"""
Convenience classes
"""


class InvalidAuthError(UnauthorizedError):
    pass


class InvalidJWTError(UnauthorizedError):
    pass


class AccessTokenExpiredError(UnauthorizedError):
    pass


class InvalidSignatureError(BadRequestError):
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


class UnexpectedMissingValue(Exception):
    pass


class OpenAIDataError(Exception):
    pass


class SlackDataError(Exception):
    pass


class ConfluenceDataError(Exception):
    pass


class SecretRetrievalError(Exception):
    pass


class RuntimeConfigRetrievalError(Exception):
    pass
