from cryptography.exceptions import InvalidSignature

class InternalServerError(Exception):
    pass

class UnauthorizedError(Exception):
    pass

class BadRequestError(Exception):
    pass

class InvalidChecksumError(Exception):
    pass

class InvalidAuthError(UnauthorizedError):
    pass

class InvalidJWTError(UnauthorizedError):
    pass

class InvalidSignatureError(BadRequestError):
    pass

class MaxRetryAttemptsReachedError(InternalServerError):
    pass

