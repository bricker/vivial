import contextvars
import types
from collections.abc import Callable
from typing import Any

def setstatprofile(
    target: Callable[[types.FrameType, str, Any], Any] | None,
    interval: float = 0.001,
    context_var: contextvars.ContextVar[object | None] | None = None,
    timer_func: Callable[[], float] | None = None,
) -> None: ...
def get_frame_info(frame: types.FrameType) -> str: ...
def begin_tracing(dir: str) -> None: ...
def config_tracememory() -> None: ...

__version__: str
