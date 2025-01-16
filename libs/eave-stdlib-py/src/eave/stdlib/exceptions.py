from collections.abc import Callable, Generator, Mapping
import contextlib
from types import TracebackType
from typing import Any, override

from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER



class conditional_suppress(contextlib.suppress):  # noqa: N801 - following context manager naming convention
    """Context manager to _conditionally_ suppress specified exceptions

    After the exception is suppressed, execution proceeds with the next
    statement following the with statement.

         with suppress(FileNotFoundError):
             os.remove(somefile)
         # Execution still resumes here if the file was already removed
    """

    _condition: bool | Callable[[], bool] | None
    _silent: bool
    _ctx: Mapping[str, Any] | None

    def __init__(self, *exceptions: type[BaseException], condition: bool | Callable[[], bool] | None = None, silent: bool = False, ctx: Mapping[str, Any] | None = None) -> None:
        self._exceptions = exceptions
        self._condition = condition
        self._silent = silent

    @override
    def __exit__(self, exctype: type[BaseException] | None , excinst: BaseException | None, exctb: TracebackType | None) -> bool:
        should_suppress = super().__exit__(exctype, excinst, exctb)

        # If there is no exception or the exception doesn't match a passed-in exception, then always raise.
        # Otherwise, if there was an exception and it matches a passed-in exception, and a condition was given,
        # then we should additionally check the given condition.
        if should_suppress and self._condition is not None:
            if isinstance(self._condition, Callable):
                should_suppress = self._condition()
            else:
                should_suppress = self._condition

        # If errors should be logged (silent=False) and we're suppressing this error, then log the exception.
        # If errors should not be logged (silent=False), then don't log the error.
        # If we're not suppressing the error, then it will be raised normally and handled by the caller.
        if not self._silent and should_suppress and excinst is not None:
            LOGGER.exception(excinst, self._ctx)

        return should_suppress

class suppress_in_production(conditional_suppress):  # noqa: N801 - following context manager naming convention
    """
    In production, exceptions will be logged but won't raise.
    In local environments, the exceptions will always raise.
    The purpose is to loudly raise exceptions and halt execution in local environments, but continue execution in production.
    This isn't appropriate for everything; it's most valuable when dealing with external dependencies (eg APIs) where
    failures are being handled gracefully (eg with fallbacks).
    """
    def __init__(self, *exceptions: type[BaseException], ctx: Mapping[str, Any] | None = None) -> None:
        super().__init__(*exceptions, condition=(not SHARED_CONFIG.is_local), silent=False, ctx=ctx)
