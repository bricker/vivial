from collections.abc import Callable
from types import CodeType
from typing import Any

from ..config import EaveConfig


def trace_call(config: EaveConfig, code: CodeType, instruction_offset: int, func: Callable, arg0: object) -> Any:
    """
    https://docs.python.org/3.12/library/sys.monitoring.html#callback-function-arguments
    """
    # print(inspect.signature(func))
    # print(inspect.getcallargs(func))
