from typing import Union
from starlette.responses import Response as _StarletteResponse
from starlette.requests import Request as _StarletteRequest
from werkzeug.wrappers import Response as _WerkzeugResponse, Request as _WerkzeugRequest


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
