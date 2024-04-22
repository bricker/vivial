import json
from typing import Any, Union
import uuid


JsonScalar = str | int | bool | None
JsonValue = Union[JsonScalar, "JsonObject", "JsonArray"]
JsonObject = dict[str, JsonValue]
JsonArray = list[JsonValue]

def _serializer(obj: Any) -> Any:
    if isinstance(obj, uuid.UUID):
        return obj.hex
    else:
        return obj

def compact_json(data: JsonObject) -> str:
    return json.dumps(data, indent=None, separators=(",", ":"), default=_serializer)
