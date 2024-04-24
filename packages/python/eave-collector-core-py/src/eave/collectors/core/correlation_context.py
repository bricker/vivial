import threading
import typing


class CorrelationContext:
    def __init__(self):
        thread_local = threading.local()
        thread_local.eave = {"context": {}}
        self._storage = thread_local.eave

    def get(self, key: str) -> typing.Any:
        return self._storage.get(key, None) or self._storage.get("context", {}).get(key, None)

    def set(self, key: str, value: typing.Any) -> None:
        self._storage["context"][key] = value


corr_ctx = CorrelationContext()
