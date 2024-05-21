import contextvars
import typing
import urllib.parse

from .base import COOKIE_PREFIX, BaseCorrelationContext

_local_async_storage = contextvars.ContextVar("eave_corr_ctx")


class AsyncioCorrelationContext(BaseCorrelationContext):
    received_context_key = "received"
    updated_context_key = "updated"

    def _get_storage(self) -> dict[str, typing.Any]:
        eave_ctx = contextvars.copy_context().get(_local_async_storage, None)
        if not eave_ctx:
            _local_async_storage.set(
                {
                    self.received_context_key: {},
                    self.updated_context_key: {},
                }
            )
            # refetch ctx vars now that we've set a value
            eave_ctx = contextvars.copy_context().get(_local_async_storage)
        return typing.cast(dict[str, typing.Any], eave_ctx)

    def get(self, key: str) -> str:
        storage = self._get_storage()
        updated_value = storage.get(self.updated_context_key, {}).get(key, None)
        if updated_value is not None:
            return updated_value
        return storage.get(self.received_context_key, {}).get(key, None)

    def set(self, key: str, value: str) -> None:
        storage = self._get_storage()
        storage[self.updated_context_key][key] = value

    def to_dict(self) -> dict[str, str]:
        storage = self._get_storage()
        # merge received and updated values together
        ctx_data = storage.get(self.received_context_key, {}).copy()
        ctx_data.update(storage.get(self.updated_context_key, {}))
        return ctx_data

    def get_updated_values_cookies(self) -> list[str]:
        storage = self._get_storage()
        # URL encode the cookie values
        # TODO: cookie settings? expiration?
        return [
            f"{self._ensure_prefix(key)}={self._cookify(value)}"
            for key, value in storage[self.updated_context_key].items()
        ]

    def from_cookies(self, cookies: dict[str, str]) -> None:
        storage = self._get_storage()
        for cookie_name, value in [(k, v) for k, v in cookies.items() if k.startswith(COOKIE_PREFIX)]:
            # URL decode cookie values
            decoded_value = urllib.parse.unquote(value)
            storage[self.received_context_key][cookie_name] = decoded_value
