import asyncio
import logging
from functools import wraps
from typing import (
    Any,
    Awaitable,
    Callable,
    Concatenate,
    Coroutine,
    ParamSpec,
    ParamSpecKwargs,
    Type,
    TypeVar,
    cast,
)

logger = logging.getLogger("eave-stdlib-py")

JsonScalar = str | int | bool | None
JsonObject = dict[str, Any]

P = ParamSpec("P")
T = TypeVar("T")


def sync_memoized(f: Callable[..., T]) -> Callable[..., T]:
    @wraps(f)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> T:
        if not hasattr(self, "__memo__"):
            # FIXME: This is not threadsafe
            self.__memo__ = dict[str, Any]()

        memokey = f.__name__
        if memokey in self.__memo__:
            memoval: T = self.__memo__[memokey]
            return memoval

        value: T = f(self, *args, **kwargs)
        self.__memo__[memokey] = value
        return value

    return wrapper


def memoized(f: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    @wraps(f)
    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> T:
        if hasattr(self, "__memo__") is False:
            # FIXME: This is not threadsafe
            self.__memo__ = dict[str, Any]()

        memokey = f.__name__
        if memokey in self.__memo__:
            memoval: T = self.__memo__[memokey]
            return memoval

        value: T = await f(self, *args, **kwargs)
        self.__memo__[memokey] = value
        return value

    return wrapper


def use_signature(source_func: Callable[P, Any]) -> Callable[[Callable[..., T]], Callable[P, T]]:
    """Casts the decorated function to have the same signature as the source function, for type checkers"""

    def casted_func(original_func: Callable[..., T]) -> Callable[P, T]:
        return cast(Callable[P, T], original_func)

    return casted_func


tasks = set[asyncio.Task[Any]]()


def do_in_background(coro: Coroutine[Any, Any, T]) -> asyncio.Task[T]:
    task = asyncio.create_task(coro)
    tasks.add(task)
    task.add_done_callback(tasks.discard)
    return task
