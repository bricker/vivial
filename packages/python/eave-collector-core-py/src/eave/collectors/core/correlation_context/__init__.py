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
    import os
    import sys

    # check if process args include any hints at webserver running the app
    for arg in sys.argv:
        if "uvicorn" in arg or "daphne" in arg or "hypercorn" in arg:
            return AsyncioCorrelationContext()
        if "gunicorn" in arg or "uwsgi" in arg:
            return ThreadedCorrelationContext()

    if "uwsgi" in sys.modules or "mod_wsgi" in sys.modules:
        return ThreadedCorrelationContext()

    server_software = os.getenv("SERVER_SOFTWARE", "").lower()
    if "gunicorn" in server_software:
        return ThreadedCorrelationContext()

    # fallback to threaded
    from eave.collectors.core.logging import EAVE_LOGGER
    EAVE_LOGGER.warning("Eave unable to determine application webserver, falling back to WSGI context handler")
    return ThreadedCorrelationContext()


corr_ctx = _correlation_context_factory()
