from types import CodeType
from typing import Any

from eave.monitoring.python.config import EaveConfig
from .util import DISABLE


def trace_branch(config: EaveConfig, code: CodeType, instruction_offset: int, destination_offset: int) -> Any:
    """
    https://docs.python.org/3.12/library/sys.monitoring.html#callback-function-arguments
    """
    pass
