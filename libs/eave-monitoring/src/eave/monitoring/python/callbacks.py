import functools
from datetime import date, datetime
import inspect
import re
import sys
from types import CodeType
from typing import Any, Callable, Concatenate
from uuid import uuid4
from eave.stdlib.pytracing import client

from eave.stdlib.pytracing.config import EaveConfig

from .datastructures import EventType, FunctionCallEventParams, RawEvent

DISABLE = sys.monitoring.DISABLE

_builtins_set = set(sys.builtin_module_names)
_stdlib_set = sys.stdlib_module_names
_common_noisy_modules_to_ignore = set(
    (
        "pydantic",
        "pkg_resources",
    )
)

_ignore_modules_set = _builtins_set | _stdlib_set | _common_noisy_modules_to_ignore

# FIXME: support list, tuple, and dict; may contain unpickleable objects.
_primitive_types = (bool, str, int, float, date, datetime, type(None))


def eave_tracer[
    **P, R
](config: EaveConfig) -> Callable[[Callable[Concatenate[EaveConfig, P], R],], Callable[P, R]]:
    def inner0(f: Callable[Concatenate[EaveConfig, P], R]) -> Callable[P, R]:
        @functools.wraps(f)
        def inner1(*args: P.args, **kwargs: P.kwargs) -> R:
            return f(config, *args, **kwargs)

        return inner1

    return inner0


def trace_call(config: EaveConfig, code: CodeType, instruction_offset: int, func: Callable, arg0: object) -> Any:
    pass
    # print(inspect.signature(func))
    # print(inspect.getcallargs(func))


def trace_py_start(config: EaveConfig, code: CodeType, instruction_offset: int) -> Any:
    if not inspect or not sys or not re:
        # uninitialized modules
        return DISABLE

    module = inspect.getmodule(code)
    if not module:
        return DISABLE

    if _should_ignore_module(name=module.__name__, scope=config.scope):
        # print("ignored module", module.__name__)
        return DISABLE

    if _should_ignore_module(name=module.__package__, scope=config.scope):
        # print("ignored package", module.__package__)
        return DISABLE

    # https://docs.python.org/3/reference/datamodel.html#frame-objects
    # _getframe(2) gives us the caller of the function being traced
    frame = sys._getframe(2)
    if not frame:
        return DISABLE

    # https://docs.python.org/3/reference/datamodel.html#code-objects
    if code.co_name.startswith("_"):
        # Skip "private" methods and dunder methods
        # TODO: Is this okay?
        # print("ignored private/dunder method", code.co_name)
        return DISABLE

    # print(module.__name__, module.__package__, code.co_name, scope)

    # co_argcount includes co_posonlyargcount, but does _not_ include co_kwonlyargcount. It also doesn't include *args and **kwargs.
    namedargscount = code.co_argcount + code.co_kwonlyargcount
    argnames = code.co_varnames[:namedargscount]
    argvals = {
        k: v for k, v in frame.f_locals.items() if k in argnames and k != "self" and isinstance(v, _primitive_types)
    }

    # nonprimitives = {k: v for k, v in frame.f_locals.items() if k in argnames and k != "self" and not isinstance(v, _primitive_types)}
    # print(nonprimitives)
    # if len(argvals) > 0:
    #     print(argvals)

    fclassname = code.__class__.__name__ if hasattr(code, "__class__") else None

    team_id = uuid4()
    corr_id = uuid4()
    timestamp = datetime.utcnow()

    data = RawEvent(
        team_id=team_id,
        corr_id=corr_id,
        timestamp=timestamp,
        event_type=EventType.functioncall,
        event_params=FunctionCallEventParams(
            function_module=module.__name__,
            function_class=fclassname,
            function_name=code.co_name,
            function_args=argvals,
        ),
    )

    client.send(data)
    # write_queue.put(data)


def trace_py_return(code: CodeType, instruction_offset: int, retval: object) -> Any:
    return DISABLE


def trace_branch(code: CodeType, instruction_offset: int, destination_offset: int) -> Any:
    return DISABLE


def _should_ignore_module(name: str | None, scope: str | None) -> bool:
    if not name:
        return False

    elif name in _ignore_modules_set:
        return True

    elif name.startswith("_"):
        # ignore "private" modules, eg "_pytest"
        # TODO: Is this okay?
        return True

    elif scope and not name.startswith(scope):
        # A scope was provided; if the code's module isn't within the scope, bypass
        return True

    else:
        return False
