from datetime import datetime
import json
import uuid
from typing import Any, Union

JsonScalar = str | int | float | bool | None
JsonValue = Union[JsonScalar, "JsonObject", "JsonArray"]
JsonObject = dict[str, JsonValue]
JsonArray = list[JsonValue]


class DatabaseTypesJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, uuid.UUID):
            return str(o)
        elif isinstance(o, datetime):
            return o.timestamp()
        else:
            super().default(o)


def compact_json(data: JsonObject) -> str:
    return json.dumps(data, indent=None, separators=(",", ":"), cls=DatabaseTypesJSONEncoder)
