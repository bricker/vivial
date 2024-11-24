from http import HTTPStatus

"""
Convenience classes for raising an error with a specific error code.
Errors that inherit HTTPError are intended to be handled as HTTP errors. For example, if a resource isn't found,
an HTTPError may be raised with status code 404. In this case, no error is logged in our monitoring systems.
Most errors that do not inherit HTTPError aren't specifically handled anywhere and will show up in our error logs.
Errors like this should just be thrown, and let the middleware handle logging.
"""


class HTTPError(Exception):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR


class BadRequestError(HTTPError):
    status_code = HTTPStatus.BAD_REQUEST


class UnauthorizedError(HTTPError):
    status_code=HTTPStatus.UNAUTHORIZED


class ForbiddenError(HTTPError):
    status_code=HTTPStatus.FORBIDDEN


class NotFoundError(HTTPError):
    status_code=HTTPStatus.NOT_FOUND


class LengthRequiredError(HTTPError):
    status_code=HTTPStatus.LENGTH_REQUIRED


class RequestEntityTooLargeError(HTTPError):
    status_code=HTTPStatus.REQUEST_ENTITY_TOO_LARGE


class UnprocessableEntityError(HTTPError):
    status_code=HTTPStatus.UNPROCESSABLE_ENTITY


class InternalServerError(HTTPError):
    status_code=HTTPStatus.INTERNAL_SERVER_ERROR
