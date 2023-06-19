JsonScalar = str | int | bool | None
JsonObject = dict[str, "JsonValue"]
JsonArray = list["JsonValue"]
JsonValue = JsonScalar | JsonObject | JsonArray
