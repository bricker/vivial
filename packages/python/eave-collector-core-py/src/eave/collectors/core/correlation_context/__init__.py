import os
import sys

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
    for arg in sys.argv:
        cleaned_arg = arg.lower()
        if "uvicorn" in cleaned_arg or "daphne" in cleaned_arg or "hypercorn" in cleaned_arg:
            return AsyncioCorrelationContext()

    for arg in sys.argv:
        cleaned_arg = arg.lower()
        if "gunicorn" in cleaned_arg or "uwsgi" in cleaned_arg:
            return ThreadedCorrelationContext()

    if "uwsgi" in sys.modules or "mod_wsgi" in sys.modules:
        return ThreadedCorrelationContext()

    server_software = os.getenv("SERVER_SOFTWARE", "").lower()
    if "gunicorn" in server_software:
        return ThreadedCorrelationContext()

    EAVE_LOGGER.warning("Eave unable to determine application webserver, falling back to WSGI context handler")
    return ThreadedCorrelationContext()


CORR_CTX = _correlation_context_factory()
