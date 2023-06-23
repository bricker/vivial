from typing import Union


JsonScalar = str | int | bool | None
JsonValue = Union[JsonScalar, "JsonObject", "JsonArray"]
JsonObject = dict[str, JsonValue]
JsonArray = list[JsonValue]
