from datetime import datetime
import inspect
import re
import sys
from types import CodeType
from typing import Any
from uuid import uuid4

from eave.stdlib.task_queue import do_in_background

from .datastructures import EventType, FunctionCallEventParams, RawEvent
from .write_queue import write_queue

# https://docs.python.org/3.12/library/sys.monitoring.html#callback-function-arguments

DISABLE = sys.monitoring.DISABLE

def trace_call(code: CodeType, instruction_offset: int, func: object, arg0: object) -> Any:
    if not re or not sys:
        # uninitialized module
        return DISABLE

    if not re.search("eave-monorepo/libs/eave-stdlib-py", code.co_filename):
        return DISABLE

def trace_py_start(code: CodeType, instruction_offset: int) -> Any:
    if not inspect or not sys or not re:
        return DISABLE

    frame = inspect.currentframe()
    if not frame:
        return DISABLE

    if not re.search("eave-monorepo/libs/eave-stdlib-py", code.co_filename):
        return DISABLE

    argnames = (
        code.co_varnames[:code.co_argcount]
        + code.co_varnames[:code.co_kwonlyargcount]
        + code.co_varnames[:code.co_kwonlyargcount]
    )

    argvals = {k: v for k, v in frame.f_locals.items() if k in argnames}

    fmodule = code.__module__ if hasattr(code, "__module__") else None
    fclass = code.__class__ if hasattr(code, "__class__") else None
    fclassname = fclass.__name__ if hasattr(fclass, "__name__") else None

    # print(
    #     "> [trace]", code.co_name,
    #     "\n\t> filename", code.co_filename,
    #     "\n\t> co_firstlineno", code.co_firstlineno,
    #     "\n\t> module", fmodule,
    #     "\n\t> fclassname", fclassname,
    #     "\n\t> argvals", argvals,
    #     "\n\n",
    # )

    team_id = uuid4()
    corr_id = uuid4()
    timestamp=datetime.now()

    data = RawEvent(
        team_id=team_id,
        corr_id=corr_id,
        timestamp=timestamp,
        event_type=EventType.functioncall,
        event_params=FunctionCallEventParams(
            function_module=fmodule,
            function_class=fclassname,
            function_name=code.co_name,
            function_args=argvals,
        ),
    )

    write_queue.put(data)

def trace_py_return(code: CodeType, instruction_offset: int, retval: object) -> Any:
    return DISABLE

def trace_branch(code: CodeType, instruction_offset: int, destination_offset: int) -> Any:
    return DISABLE
