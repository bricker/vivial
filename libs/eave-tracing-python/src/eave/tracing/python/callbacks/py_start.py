import inspect
import re
import sys
from datetime import datetime
from types import CodeType
from typing import Any
from uuid import uuid4

from ..config import EaveConfig
from .util import DISABLE, PRIMITIVE_TYPES, should_ignore_module


def trace_py_start(config: EaveConfig, code: CodeType, instruction_offset: int) -> Any:
    """
    https://docs.python.org/3.12/library/sys.monitoring.html#callback-function-arguments
    """
    if not inspect or not sys or not re:
        # uninitialized modules
        return DISABLE

    module = inspect.getmodule(code)
    if not module:
        return DISABLE

    if should_ignore_module(name=module.__name__, scope=config.scope):
        # print("ignored module", module.__name__)
        return DISABLE

    if should_ignore_module(name=module.__package__, scope=config.scope):
        # print("ignored package", module.__package__)
        return DISABLE

    # https://docs.python.org/3/reference/datamodel.html#frame-objects
    # _getframe(2) gives us the caller of the function being traced
    frame = sys._getframe(2)  # noqa: SLF001
    if not frame:
        return DISABLE

    # print(module.__name__, module.__package__, code.co_name, scope)

    # co_argcount includes co_posonlyargcount, but does _not_ include co_kwonlyargcount. It also doesn't include *args and **kwargs.
    namedargscount = code.co_argcount + code.co_kwonlyargcount
    argnames = code.co_varnames[:namedargscount]
    _argvals = {
        k: v for k, v in frame.f_locals.items() if k in argnames and k != "self" and isinstance(v, PRIMITIVE_TYPES)
    }

    # nonprimitives = {k: v for k, v in frame.f_locals.items() if k in argnames and k != "self" and not isinstance(v, _primitive_types)}
    # print(nonprimitives)
    # if len(argvals) > 0:
    #     print(argvals)

    _fclassname = code.__class__.__name__ if hasattr(code, "__class__") else None

    _team_id = uuid4()
    _corr_id = uuid4()
    _timestamp = datetime.utcnow()

    # data = RawEvent(
    #     team_id=team_id,
    #     corr_id=corr_id,
    #     timestamp=timestamp,
    #     event_type=EventType.functioncall,
    #     event_params=FunctionCallEventParams(
    #         function_module=module.__name__,
    #         function_class=fclassname,
    #         function_name=code.co_name,
    #         function_args=argvals,
    #     ),
    # )

    # client.send(data)
    # write_queue.put(data)
