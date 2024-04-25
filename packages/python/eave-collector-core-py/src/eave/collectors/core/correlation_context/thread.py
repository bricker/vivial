import json
import threading
import typing

from .base import BaseCorrelationContext

# TODO: customer child threads wont share this storage
_local_thread_storage = threading.local()


class ThreadedCorrelationContext(BaseCorrelationContext):
    def _init_storage(self) -> None:
        if not getattr(_local_thread_storage, "eave", None):
            _local_thread_storage.eave = {"context": {}}

    def get(self, key: str) -> typing.Any:
        self._init_storage()
        return _local_thread_storage.eave.get(key, None) or _local_thread_storage.eave.get("context", {}).get(key, None)

    def set(self, key: str, value: typing.Any) -> None:
        self._init_storage()
        _local_thread_storage.eave["context"][key] = value

    def to_json(self) -> str:
        self._init_storage()
        return json.dumps(_local_thread_storage.eave)
