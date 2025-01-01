from typing import Any, Literal, TypeAlias, Union, override

from starlette.requests import Request as _StarletteRequest
from starlette.responses import Response as _StarletteResponse

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | JsonObject | JsonArray
type JsonObject = dict[str, JsonValue]
type JsonArray = list[JsonValue]

type StarletteRequest = _StarletteRequest
type StarletteResponse = _StarletteResponse

type HTTPFrameworkRequest = StarletteRequest
type HTTPFrameworkResponse = StarletteResponse


class NotSet:
    """
    A sentinel singleton class used to distinguish omitted keyword arguments
    from those passed in with the value None (which may have different behavior).

    For example:

    ```py
    def get(timeout: Union[int, NotGiven, None] = NotGiven()) -> Response:
        ...


    get(timeout=1)  # 1s timeout
    get(timeout=None)  # No timeout
    get()  # Default timeout behavior, which may not be statically known at the method definition.
    ```

    Copied from openai-python
    """

    def __bool__(self) -> Literal[False]:
        return False

    @override
    def __repr__(self) -> str:
        return "NOT_SET"


NOT_SET: Any = NotSet()
