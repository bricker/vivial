import json
import threading
import typing

# TODO: doesnt work w/ async dispatch.. but that's tough anywayu bcus we want to persiste across user-space async dispatch
# TODO: customer child threads wont share this storage
_storage = threading.local()


class CorrelationContext:
    def __init__(self):
        self._init_storage()

    def _init_storage(self) -> None:
        if not getattr(_storage, "eave", None):
            _storage.eave = {"context": {}}

    def get(self, key: str) -> typing.Any:
        self._init_storage()
        return _storage.eave.get(key, None) or _storage.eave.get("context", {}).get(key, None)

    def set(self, key: str, value: typing.Any) -> None:
        self._init_storage()
        _storage.eave["context"][key] = value

    def to_json(self) -> str:
        self._init_storage()
        return json.dumps(_storage.eave)


corr_ctx = CorrelationContext()
