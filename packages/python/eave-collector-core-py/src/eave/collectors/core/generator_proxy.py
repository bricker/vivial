from collections.abc import Callable
from typing import Any, Self


class GeneratorProxy:
    def __init__(self, gen: Any, completion_handler: Callable[[Any], None], error_handler: Callable) -> None:
        self._gen = gen
        self._completion_handler = completion_handler
        self._error_handler = error_handler
        self._prev_value = None

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> None:
        return_val = None
        try:
            return_val = self._gen.__next__()
            self._prev_value = return_val
        except StopIteration:
            self._completion_handler(self._prev_value)
            raise
        except Exception:
            self._error_handler()
            raise
        return return_val


class AsyncGeneratorProxy:
    def __init__(self, gen: Any, completion_handler: Callable[[Any], None], error_handler: Callable) -> None:
        self._gen = gen
        self._completion_handler = completion_handler
        self._error_handler = error_handler
        self._prev_value = None

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> None:
        return_val = None
        try:
            return_val = await self._gen.__next__()
            self._prev_value = return_val
        except StopIteration:
            self._completion_handler(self._prev_value)
            raise
        except Exception:
            self._error_handler()
            raise
        return return_val
