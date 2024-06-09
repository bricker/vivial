from dataclasses import dataclass
import threading
import typing
import urllib.parse

from .base import COOKIE_PREFIX, BaseCorrelationContext, CorrCtxStorage

# TODO: customer child threads wont share this storage
_local_thread_storage = threading.local()

class ThreadedCorrelationContext(BaseCorrelationContext):
    def _init_storage(self) -> None:
        _local_thread_storage.eave = CorrCtxStorage()

    def _lazy_init_storage(self) -> CorrCtxStorage:
        if not hasattr(_local_thread_storage, "eave"):
            self._init_storage()

        return _local_thread_storage.eave

    def get(self, key: str) -> str | None:
        storage = self._lazy_init_storage()
        updated_value = storage.updated.get(key)
        if updated_value is not None:
            return updated_value
        return storage.received.get(key)

    def set(self, key: str, value: str) -> None:
        storage = self._lazy_init_storage()
        storage.updated[key] = str(value)

    def to_dict(self) -> dict[str, str]:
        storage = self._lazy_init_storage()
        return storage.merged()

    def get_updated_values_cookies(self) -> list[str]:
        storage = self._lazy_init_storage()
        # URL encode the cookie value
        # TODO: cookie settings? expiration?
        return [
            f"{self._ensure_prefix(key)}={self._cookify(value)}"
            for key, value in storage.updated.items()
        ]

    def from_cookies(self, cookies: dict[str, str]) -> None:
        storage = self._lazy_init_storage()
        for cookie_name, value in [(k, v) for k, v in cookies.items() if k.startswith(COOKIE_PREFIX)]:
            # URL decode cookie values
            decoded_value = urllib.parse.unquote(value)
            storage.received[cookie_name] = decoded_value

    def clear(self) -> None:
        self._init_storage()
