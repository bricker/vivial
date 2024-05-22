import threading
import typing
import urllib.parse

from .base import COOKIE_PREFIX, BaseCorrelationContext

# TODO: customer child threads wont share this storage
_local_thread_storage = threading.local()


class ThreadedCorrelationContext(BaseCorrelationContext):
    received_context_key = "received"
    updated_context_key = "updated"

    def _init_storage(self) -> None:
        _local_thread_storage.eave = {
            self.received_context_key: {},
            self.updated_context_key: {},
        }

    def _lazy_init_storage(self) -> None:
        if not getattr(_local_thread_storage, "eave", None):
            self._init_storage()

    def get(self, key: str) -> str:
        self._lazy_init_storage()
        updated_value = _local_thread_storage.eave.get(self.updated_context_key, {}).get(key, None)
        if updated_value is not None:
            return updated_value
        return _local_thread_storage.eave.get(self.received_context_key, {}).get(key, None)

    def set(self, key: str, value: str) -> None:
        self._lazy_init_storage()
        _local_thread_storage.eave[self.updated_context_key][key] = str(value)

    def to_dict(self) -> dict[str, typing.Any]:
        self._lazy_init_storage()
        # merge received and updated values together
        ctx_data = _local_thread_storage.eave.get(self.received_context_key, {}).copy()
        ctx_data.update(_local_thread_storage.eave.get(self.updated_context_key, {}))
        return ctx_data

    def get_updated_values_cookies(self) -> list[str]:
        self._lazy_init_storage()
        # URL encode the cookie value
        # TODO: cookie settings? expiration?
        return [
            f"{self._ensure_prefix(key)}={self._cookify(value)}"
            for key, value in _local_thread_storage.eave[self.updated_context_key].items()
        ]

    def from_cookies(self, cookies: dict[str, str]) -> None:
        self._lazy_init_storage()
        for cookie_name, value in [(k, v) for k, v in cookies.items() if k.startswith(COOKIE_PREFIX)]:
            # URL decode cookie values
            decoded_value = urllib.parse.unquote(value)
            _local_thread_storage.eave[self.received_context_key][cookie_name] = decoded_value

    def clear(self) -> None:
        self._init_storage()
