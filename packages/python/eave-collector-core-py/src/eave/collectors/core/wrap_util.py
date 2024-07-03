from collections.abc import Callable, Coroutine
from typing import Any

from wrapt import patch_function_wrapper

WRAPPED_TAG = "_eave_wrapped"
def tag_wrapped(obj: object) -> None:
    try:
        setattr(obj, WRAPPED_TAG, True)
    except AttributeError:
        pass

def untag_wrapped(obj: object) -> None:
    try:
        delattr(obj, WRAPPED_TAG)
    except AttributeError:
        pass

def is_wrapped(obj: object) -> bool:
    return getattr(obj, WRAPPED_TAG, False) is True


def wrap[T, **P](
    module: str,
    name: str,
    wrapper: Callable[[Callable[P, T], Any, tuple[Any, ...], dict[str, Any]], T],
    check_enabled: Callable[[], bool] | None = None,
) -> None:
    patch_function_wrapper(
        module=module,
        name=name,
        enabled=check_enabled
        if check_enabled is not None
        else True,  # Default to always enabled. The enabled param accepts a callable or a boolean.
    )(wrapper=wrapper)


def wrap_async[T, **P](
    module: str,
    name: str,
    wrapper: Callable[
        [Callable[P, Coroutine[Any, Any, T]], Any, tuple[Any, ...], dict[str, Any]], Coroutine[Any, Any, T]
    ],
    check_enabled: Callable[[], bool] | None = None,
) -> None:
    patch_function_wrapper(
        module=module,
        name=name,
        enabled=check_enabled
        if check_enabled is not None
        else True,  # Default to always enabled. The enabled param accepts a callable or a boolean.
    )(wrapper=wrapper)


# # Copied from opentelemetry-python-contrib
# def unwrap(obj: object, attr: str) -> None:
#     """Given a function that was wrapped by wrapt.wrap_function_wrapper, unwrap it

#     Args:
#         obj: Object that holds a reference to the wrapped function
#         attr (str): Name of the wrapped function
#     """
#     func = getattr(obj, attr, None)
#     if func and isinstance(func, ObjectProxy) and hasattr(func, "__wrapped__"):
#         setattr(obj, attr, func.__wrapped__)
