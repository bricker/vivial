from _typeshed import TraceFunction
from types import FrameType
from typing import Any, Optional


def eave_tracefunc(frame: FrameType, event: str, arg: Any) -> Optional["TraceFunction"]:
    ...
