from functools import reduce
import inspect
import sys
from typing import Any, Callable
from .callbacks import trace_call, trace_py_start, scoped
from .write_queue import write_queue
from .pg_trace import start_postgresql_listener

_tool_id = 0

# https://docs.python.org/3.12/library/sys.monitoring.html#events

_events: dict[int, Callable[..., Any]] = {
    # sys.monitoring.events.CALL: trace_call,
    sys.monitoring.events.PY_START: trace_py_start,
    # sys.monitoring.events.PY_RETURN: trace_py_return,
}

_events_mask = reduce(lambda a, b: a | b, _events.keys())

def start_tracing(scope: str | None = None) -> None:
    """
    Start automatic tracing for analytics.

    * scope: A module or package name prefix to scope tracing to. For example, passing `eave.stdlib` will only trace code in the `eave.stdlib` package. If set to None (default), the calling module will be used. The scope improves performance by ignoring irrelevant code. If you want to turn off scoping (not recommended), pass an empty string.
    """
    if scope is None:
        if (frame := inspect.currentframe()) and (back := frame.f_back) and (tracemodule := inspect.getmodule(back.f_code)):
            scope = tracemodule.__package__

    sys.monitoring.use_tool_id(_tool_id, "eave")

    for event, callback in _events.items():
        func = scoped(scope=scope)(callback)
        sys.monitoring.register_callback(_tool_id, event, func)

    sys.monitoring.set_events(_tool_id, _events_mask)
    write_queue.start_autoflush()

def stop_tracing() -> None:
    sys.monitoring.set_events(_tool_id, 0)

    for event in _events:
        sys.monitoring.register_callback(_tool_id, event, None)

    sys.monitoring.free_tool_id(_tool_id)
    write_queue.stop_autoflush()
