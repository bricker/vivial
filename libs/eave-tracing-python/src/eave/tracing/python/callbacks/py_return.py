from types import CodeType
from typing import Any
from .util import DISABLE
from ..config import EaveConfig


def trace_py_return(config: EaveConfig, code: CodeType, instruction_offset: int, retval: object) -> Any:
    """
    https://docs.python.org/3.12/library/sys.monitoring.html#callback-function-arguments
    """
    pass
