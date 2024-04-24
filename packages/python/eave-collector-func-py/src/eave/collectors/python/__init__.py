import functools
import inspect
import sys
from collections.abc import Callable
from functools import reduce
from typing import Any, Concatenate, Optional

from eave.collectors.python.callbacks.branch import trace_branch
from eave.collectors.python.callbacks.call import trace_call
from eave.collectors.python.callbacks.line import trace_line
from eave.collectors.python.callbacks.py_return import trace_py_return
from eave.collectors.python.callbacks.py_start import trace_py_start

from .config import EaveConfig

_TOOL_ID = 0
_TOOL_NAME = "eave"

# https://docs.python.org/3.12/library/sys.monitoring.html#events

_events: dict[int, Callable[Concatenate[EaveConfig, ...], Any] | None] = {
    sys.monitoring.events.BRANCH: trace_branch,
    sys.monitoring.events.CALL: trace_call,
    sys.monitoring.events.C_RAISE: None,
    sys.monitoring.events.C_RETURN: None,
    sys.monitoring.events.EXCEPTION_HANDLED: None,
    sys.monitoring.events.INSTRUCTION: None,
    sys.monitoring.events.JUMP: None,
    sys.monitoring.events.LINE: trace_line,
    sys.monitoring.events.NO_EVENTS: None,
    sys.monitoring.events.PY_RESUME: None,
    sys.monitoring.events.PY_RETURN: trace_py_return,
    sys.monitoring.events.PY_START: trace_py_start,
    sys.monitoring.events.PY_THROW: None,
    sys.monitoring.events.PY_UNWIND: None,
    sys.monitoring.events.PY_YIELD: None,
    sys.monitoring.events.RAISE: None,
    sys.monitoring.events.RERAISE: None,
    sys.monitoring.events.STOP_ITERATION: None,
}

_events_mask = reduce(lambda a, b: a | b, _events.keys())


def eave_tracer[**P, R](
    config: EaveConfig,
) -> Callable[
    [
        Callable[Concatenate[EaveConfig, P], R],
    ],
    Callable[P, R],
]:
    def inner0(f: Callable[Concatenate[EaveConfig, P], R]) -> Callable[P, R]:
        @functools.wraps(f)
        def inner1(*args: P.args, **kwargs: P.kwargs) -> R:
            return f(config, *args, **kwargs)

        return inner1

    return inner0


def start_tracing(
    scope: str | None = None,
) -> None:
    """
    Start automatic tracing for analytics.

    * scope: A module or package name prefix to scope tracing to. For example, passing `eave.stdlib` will only trace code in the `eave.stdlib` package. If set to None (default), the calling module will be used. The scope improves performance by ignoring irrelevant code. If you want to turn off scoping (not recommended), pass an empty string.
    """

    config = EaveConfig(scope=scope)

    if config.scope is None:
        if (
            (frame := inspect.currentframe())
            and (back := frame.f_back)
            and (tracemodule := inspect.getmodule(back.f_code))
        ):
            config.scope = tracemodule.__package__

    sys.monitoring.use_tool_id(_TOOL_ID, _TOOL_NAME)

    for event, callback in _events.items():
        if callback:
            func = eave_tracer(config=config)(callback)
            sys.monitoring.register_callback(_TOOL_ID, event, func)

    sys.monitoring.set_events(_TOOL_ID, _events_mask)
    # write_queue.start_autoflush()


def stop_tracing() -> None:
    sys.monitoring.set_events(_TOOL_ID, 0)

    for event in _events:
        sys.monitoring.register_callback(_TOOL_ID, event, None)

    sys.monitoring.free_tool_id(_TOOL_ID)
    # write_queue.stop_autoflush()
