from functools import reduce
import multiprocessing
import sys
import atexit
from typing import Any, Callable
from .callbacks import trace_call, trace_py_return, trace_py_start
from .write_queue import write_queue

_tool_id = 0
sys.monitoring.use_tool_id(_tool_id, "eave")

# https://docs.python.org/3.12/library/sys.monitoring.html#events

_events: dict[int, Callable[..., Any]] = {
    # sys.monitoring.events.CALL: trace_call,
    sys.monitoring.events.PY_START: trace_py_start,
    # sys.monitoring.events.PY_RETURN: trace_py_return,
}

_events_mask = reduce(lambda a, b: a | b, _events.keys())

def start_tracing() -> None:
    for event, callback in _events.items():
        sys.monitoring.register_callback(_tool_id, event, callback)

    sys.monitoring.set_events(_tool_id, _events_mask)
    write_queue.start_autoflush()

def stop_tracing() -> None:
    sys.monitoring.set_events(_tool_id, 0)

    for event in _events:
        sys.monitoring.register_callback(_tool_id, event, None)

    sys.monitoring.free_tool_id(_tool_id)
    write_queue.stop_autoflush()
