from starlette.middleware import Middleware

from .body_parsing import BodyParsingASGIMiddleware
from .exception_handling import ExceptionHandlingASGIMiddleware
from .logging import LoggingASGIMiddleware
from .request_integrity import RequestIntegrityASGIMiddleware

common_middlewares = [
    Middleware(ExceptionHandlingASGIMiddleware),
    Middleware(RequestIntegrityASGIMiddleware),
    Middleware(BodyParsingASGIMiddleware),
    Middleware(LoggingASGIMiddleware),
]
