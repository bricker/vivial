from typing import Literal, Union, override

from starlette.requests import Request as _StarletteRequest
from starlette.responses import Response as _StarletteResponse
from werkzeug.wrappers import Request as _WerkzeugRequest
from werkzeug.wrappers import Response as _WerkzeugResponse

JsonScalar = str | int | bool | None
JsonValue = Union[JsonScalar, "JsonObject", "JsonArray"]
JsonObject = dict[str, JsonValue]
JsonArray = list[JsonValue]

StarletteRequest = _StarletteRequest
StarletteResponse = _StarletteResponse
WerkzeugRequest = _WerkzeugRequest
WerkzeugResponse = _WerkzeugResponse

HTTPFrameworkRequest = StarletteRequest | WerkzeugRequest
HTTPFrameworkResponse = StarletteResponse | WerkzeugResponse


class NotGiven:
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
        return "NOT_GIVEN"


NOT_GIVEN = NotGiven()
