from typing import Any, Literal


JsonScalar = str | int | bool | None
JsonObject = dict[str, Any]

# This format is for Google Cloud Logging
LogContext = dict[Literal["json_fields"], JsonObject]
