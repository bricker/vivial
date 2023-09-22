from starlette.middleware import Middleware

from .logging import LoggingASGIMiddleware
from .body_parsing import BodyParsingASGIMiddleware
from .request_integrity import RequestIntegrityASGIMiddleware
from .exception_handling import ExceptionHandlingASGIMiddleware


common_middlewares = [
    Middleware(ExceptionHandlingASGIMiddleware),
    Middleware(RequestIntegrityASGIMiddleware),
    Middleware(BodyParsingASGIMiddleware),
    Middleware(LoggingASGIMiddleware),
]
