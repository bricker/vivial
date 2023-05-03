from http import HTTPStatus


class HTTPException(Exception):
    status_code: int
    message: str

    def __init__(self, status_code: int, message: str = "") -> None:
        self.status_code = status_code
        self.message = message


class BadRequestError(HTTPException):
    def __init__(self, message: str = "") -> None:
        super().__init__(status_code=HTTPStatus.BAD_REQUEST, message=message)


class UnauthorizedError(HTTPException):
    def __init__(self, message: str = "") -> None:
        super().__init__(status_code=HTTPStatus.UNAUTHORIZED, message=message)


class NotFoundError(HTTPException):
    def __init__(self, message: str = "") -> None:
        super().__init__(status_code=HTTPStatus.NOT_FOUND, message=message)


class InternalServerError(HTTPException):
    def __init__(self, message: str = "") -> None:
        super().__init__(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, message=message)


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


class MaxRetryAttemptsReachedError(InternalServerError):
    pass


class InvalidChecksumError(InternalServerError):
    pass


class DataConflictError(BadRequestError):
    pass