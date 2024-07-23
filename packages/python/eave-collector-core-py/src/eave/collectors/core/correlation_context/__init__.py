import inspect

from eave.collectors.core.logging import EAVE_LOGGER

from .async_task import AsyncioCorrelationContext as AsyncioCorrelationContext
from .base import BaseCorrelationContext
from .thread import ThreadedCorrelationContext as ThreadedCorrelationContext


def _correlation_context_factory() -> BaseCorrelationContext:
    """
    Based on our best guess of what python webserver the application is running on,
    construct the appropriate correlation context implementation to properly isolate
    context data between requests.

    WSGI servers use processes and/or threads to concurrently handle requests,
    so a `ThreadedCorrelationContext` should be constructed.
    ASGI servers use asyncio event loops and tasks to concurrently handle requests,
    so a `AsyncioCorrelationContext` should be constructed.
    """

    # check if process args include any hints at webserver running the app
    # We have to loop twice because we want to check every arg for each type of corr context.
    stack = reversed(inspect.stack())

    # server_software = os.getenv("SERVER_SOFTWARE", "").lower()
    # if "gunicorn" in server_software:
    #     return ThreadedCorrelationContext()

    is_asyncio = any("uvicorn" in frame.filename or "daphne" in frame.filename or "hypercorn" in frame.filename for frame in stack)
    if is_asyncio:
        return AsyncioCorrelationContext()
    else:
        return ThreadedCorrelationContext()

    # is_threaded = any(
    #     "gunicorn" in frame.filename
    #     or "uwsgi" in frame.filename
    #     for frame in stack
    # ) or "uwsgi" in sys.modules or "mod_wsgi" in sys.modules


    # EAVE_LOGGER.warning("Eave unable to determine application webserver, falling back to WSGI context handler")
    # return ThreadedCorrelationContext()


CORR_CTX = _correlation_context_factory()
