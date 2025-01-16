import base64
import contextlib
import hashlib
import json
import re
import uuid
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, Literal, ParamSpec, TypeVar

from eave.stdlib.typing import JsonObject, JsonValue

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


def sha256hexdigest(data: str | bytes) -> str:
    """
    sha256-hash the data (utf-8 string or bytes), and return a hex string
    """
    return hashlib.sha256(ensure_bytes(data)).hexdigest()


def b64encode(data: str | bytes, *, urlsafe: bool = False) -> str:
    """
    base64-encode the data (utf-8 string or bytes) and return an ASCII string
    """
    b = ensure_bytes(data)
    if urlsafe:
        return base64.urlsafe_b64encode(b).decode()
    else:
        return base64.b64encode(b).decode()


def b64decode(data: str | bytes, *, urlsafe: bool = False) -> str:
    """
    base64-decode the data (ASCII string or bytes) and return a utf8 string.
    Note that this function only works if you know that the encoded data will decode into a utf-8 string.
    If you are dealing with non-utf8 data, use `base64.b64decode` directly.
    """
    b = ensure_bytes(data)
    if urlsafe:
        return base64.urlsafe_b64decode(b).decode()
    else:
        return base64.b64decode(b, validate=True).decode()


def ensure_bytes(data: str | bytes | dict[str, Any]) -> bytes:
    """
    Use to reconcile some data into bytes.
    """
    if isinstance(data, dict):
        bytes = json.dumps(data).encode()
    elif isinstance(data, str):
        bytes = data.encode()
    else:
        bytes = data

    return bytes


def ensure_uuid(data: str | bytes | int | uuid.UUID | None) -> uuid.UUID:
    if isinstance(data, uuid.UUID):
        return data
    elif isinstance(data, bytes):
        return uuid.UUID(bytes=data)
    elif isinstance(data, int):
        return uuid.UUID(int=data)
    elif isinstance(data, str):
        return uuid.UUID(hex=data)
    else:
        raise TypeError(type(data))


def ensure_uuid_or_none(data: str | bytes | int | uuid.UUID | None) -> uuid.UUID | None:
    if data is None:
        return None
    else:
        return ensure_uuid(data)


def ensure_str_or_none(data: str | bytes | int | uuid.UUID | None) -> str | None:
    if data is None:
        return None
    else:
        return str(data)


def ensure_str(data: str | bytes | int | uuid.UUID | dict[str, Any]) -> str:
    if isinstance(data, str):
        return data
    elif isinstance(data, dict):
        return json.dumps(data)
    else:
        return str(data)


def compact_json(data: object, **kwargs: Any) -> str:
    """
    kwargs is forwarded to json.dumps
    """
    return json.dumps(data, indent=None, separators=(",", ":"), **kwargs)


def compact_deterministic_json(data: object, **kwargs: Any) -> str:
    """
    kwargs is forwarded to json.dumps
    """
    return json.dumps(data, indent=None, separators=(",", ":"), sort_keys=True, **kwargs)


def pretty_deterministic_json(data: object, **kwargs: Any) -> str:
    """
    kwargs is forwarded to json.dumps
    """
    return json.dumps(data, sort_keys=True, **kwargs)


def nand(a: object, b: object) -> bool:
    """Neither or one"""
    return not (bool(a) and bool(b))


def nor(a: object, b: object) -> bool:
    """Exactly neither"""
    return not (bool(a) or bool(b))


def xor(a: object, b: object) -> bool:
    """Exactly one"""
    return bool(a) ^ bool(b)


def xnor(a: object, b: object) -> bool:
    """Neither or both"""
    return not xor(a, b)


class UnwrapError(ValueError):
    pass


def unwrap(value: T | None, default: T | None = None) -> T:
    """
    Unwraps an Optional object to its wrapped type.
    You should use this method when you expect the wrapped type not to be None.
    If the object is not None, returns the unwrapped object.
    If the object is None and no default given, raises UnwrapError
    If the object is None and a default is given, logs a warning and returns the default.
    This is meant to be used when you know the object isn't None. It's a short-hand for the following verbose pattern:

        if (foo := result.get("foo")) is None:
            raise UnwrapError()

        do_something(foo)

    or, using this function:

        foo = unwrap(result.get("foo"))
        do_something(foo)

    You can optionally specify a default value, which does two things if given:
    1. Logs a warning that the default value was used
    1. Returns the default value instead of raising
    This is the "safe" version of this operation, where you want to know that an unexpected None was encountered,
    but carry on with the program. For example:

        if (foo := result.get("foo")) is None:
            LOGGER.warning("foo is None")
            foo = "default foo"

        do_something(foo)

    or, using this function:

        foo = unwrap(result.get("foo"), "default foo")
        do_something(foo)

    This is different from other default-value mechanisms because it automatically logs a warning.
    """
    if value is None:
        if default is None:
            raise UnwrapError()
        else:
            return default
    else:
        return value


def redact(string: str | None) -> str | None:
    if string is None:
        return None

    strlen = len(string)
    if strlen <= 8:
        return f"[redacted {strlen} chars]"
    return f"{string[:4]}[redacted {strlen - 8} chars]{string[-4:]}"


def erasetype(data: JsonObject, key: str, default: JsonValue | None = None) -> Any:
    if v := data.get(key, default):
        return v
    else:
        return None


def tableize(string: str) -> str:
    return re.sub(r"\W+", "_", string).lower().strip("_")


def sql_sanitized_identifier(identifier: str) -> str:
    # removes backticks and backslashes (\\\\ = 1 backslash when using normal Python string)
    i = re.sub("[`\\\\]", "", identifier)
    return f"`{i}`"


def sql_sanitized_literal(literal: str, quotechar: Literal["'", '"'] = '"') -> str:
    # removes quotes and backslashes (\\\\ = 1 backslash when using normal Python string)
    i = re.sub("['\"\\\\]", "", literal)
    return f"{quotechar}{i}{quotechar}"


def istr_eq(a: str, b: str) -> bool:
    """
    Case-insensitive comparison of two strings
    """
    return a.lower() == b.lower()


def num_with_english_suffix(num: int) -> str:
    strnum = str(num)
    if strnum.endswith(("11", "12", "13", "4", "5", "6", "7", "8", "9", "0")):
        return f"{num}th"

    elif strnum.endswith("1"):
        return f"{num}st"
    elif strnum.endswith("2"):
        return f"{num}nd"
    elif strnum.endswith("3"):
        return f"{num}rd"
    else:
        return f"{num}"
