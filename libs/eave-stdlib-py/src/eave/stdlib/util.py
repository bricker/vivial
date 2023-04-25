import asyncio
import base64
import hashlib
import logging
from functools import wraps
from typing import Any, Awaitable, Callable, Coroutine, ParamSpec, TypeVar, cast

logger = logging.getLogger("eave-stdlib-py")

JsonScalar = str | int | bool | None
JsonObject = dict[str, Any]

T = TypeVar("T")
P = ParamSpec("P")


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


def sha256hexdigest(data: str | bytes) -> str:
    """
    sha256-hash the data (utf-8 string or bytes), and return a hex string
    """
    return hashlib.sha256(ensure_bytes(data)).hexdigest()


def b64encode(data: str | bytes) -> str:
    """
    base64-encode the data (utf-8 string or bytes) and return an ASCII string
    """
    return base64.b64encode(ensure_bytes(data)).decode()


def b64decode(data: str | bytes) -> str:
    """
    base64-decode the data (ASCII string or bytes) and return a utf8 string
    """
    return base64.b64decode(ensure_bytes(data)).decode()


def ensure_bytes(data: str | bytes) -> bytes:
    """
    Use to reconcile a Union[str, bytes] parameter into bytes.
    """
    if isinstance(data, str):
        return data.encode()
    else:
        return data


tasks = set[asyncio.Task[Any]]()


def do_in_background(coro: Coroutine[Any, Any, T]) -> asyncio.Task[T]:
    task = asyncio.create_task(coro)
    tasks.add(task)
    task.add_done_callback(tasks.discard)
    return task
