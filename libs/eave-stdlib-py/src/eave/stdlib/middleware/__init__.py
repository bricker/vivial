from starlette.middleware import Middleware

from .logging import LoggingASGIMiddleware
from .body_parsing import BodyParsingASGIMiddleware
from .request_integrity import RequestIntegrityASGIMiddleware
from .exception_handling import ExceptionHandlingASGIMiddleware
from .origin import OriginASGIMiddleware
from .signature_verification import SignatureVerificationASGIMiddleware


common_middlewares = [
    Middleware(ExceptionHandlingASGIMiddleware),
    Middleware(RequestIntegrityASGIMiddleware),
    Middleware(BodyParsingASGIMiddleware),
    Middleware(LoggingASGIMiddleware),
]

common_internal_api_middlewares = [
    Middleware(OriginASGIMiddleware),
    Middleware(SignatureVerificationASGIMiddleware),
]
