from functools import wraps
from typing import Any, Callable


def memoized(f: Callable) -> Callable[..., Any]:
    @wraps(f)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if not hasattr(self, "__memo__"):
            # FIXME: This is not threadsafe
            self.__memo__ = dict[str, Any]()

        memokey = f.__name__
        if memokey in self.__memo__:
            return self.__memo__[memokey]

        value = f(self, *args, **kwargs)
        self.__memo__[memokey] = value
        return value

    return wrapper
