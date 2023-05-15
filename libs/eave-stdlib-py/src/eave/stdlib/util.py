import asyncio
import base64
import hashlib
import logging
from functools import wraps
from typing import Any, Awaitable, Callable, Coroutine, Optional, ParamSpec, TypeVar, cast
import uuid

from eave.stdlib.exceptions import UnexpectedMissingValue

logger = logging.getLogger("eave-stdlib-py")

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


def b64encode(data: str | bytes, urlsafe: bool = False) -> str:
    """
    base64-encode the data (utf-8 string or bytes) and return an ASCII string
    """
    b = ensure_bytes(data)
    if urlsafe:
        return base64.urlsafe_b64encode(b).decode()
    else:
        return base64.b64encode(b).decode()


def b64decode(data: str | bytes, urlsafe: bool = False) -> str:
    """
    base64-decode the data (ASCII string or bytes) and return a utf8 string.
    Note that this function only works if you know that the encoded data will decode into a utf-8 string.
    If you are dealing with non-utf8 data, use `base64.b64decode` directly.
    """
    b = ensure_bytes(data)
    if urlsafe:
        return base64.urlsafe_b64decode(b).decode()
    else:
        return base64.b64decode(b).decode()


def ensure_bytes(data: str | bytes) -> bytes:
    """
    Use to reconcile a Union[str, bytes] parameter into bytes.
    """
    if isinstance(data, str):
        return data.encode()
    else:
        return data


def ensure_uuid(data: str | bytes | int | uuid.UUID) -> uuid.UUID:
    if isinstance(data, uuid.UUID):
        return data
    elif isinstance(data, bytes):
        return uuid.UUID(bytes=data)
    elif isinstance(data, int):
        return uuid.UUID(int=data)
    elif isinstance(data, str):
        return uuid.UUID(hex=data)


tasks = set[asyncio.Task[Any]]()


def do_in_background(coro: Coroutine[Any, Any, T]) -> asyncio.Task[T]:
    task = asyncio.create_task(coro)
    tasks.add(task)
    task.add_done_callback(tasks.discard)
    return task


def nand(a: Any, b: Any) -> bool:
    """Neither or one"""
    return not (bool(a) and bool(b))


def nor(a: Any, b: Any) -> bool:
    """Exactly neither"""
    return not (bool(a) or bool(b))


def xor(a: Any, b: Any) -> bool:
    """Exactly one"""
    return bool(a) ^ bool(b)


def xnor(a: Any, b: Any) -> bool:
    """Neither or both"""
    return not xor(a, b)


def dict_from_obj_dict(obj: object, attrs: list[str]) -> dict[str, Any]:
    return {attr: obj.__dict__[attr] for attr in attrs if attr in obj.__dict__}


def set_obj_dict_from_dict(obj: object, allowed_attrs: list[str], provided_attrs: dict[object, object]) -> None:
    for attr in allowed_attrs:
        if attr in provided_attrs:
            obj.__dict__[attr] = provided_attrs[attr]


def dict_from_attrs(obj: object, attrs: list[str]) -> dict[str, Any]:
    return {attr: getattr(obj, attr) for attr in attrs if hasattr(obj, attr)}


def set_attrs_from_dict(obj: object, allowed_attrs: list[str], provided_attrs: dict[object, object]) -> None:
    for attr in allowed_attrs:
        if attr in provided_attrs:
            obj.__setattr__(attr, provided_attrs[attr])


def unwrap(value: Optional[T]) -> T:
    if value is None:
        raise UnexpectedMissingValue("force-unwrapped a None value")
    return value
