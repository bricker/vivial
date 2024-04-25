import contextvars
import json
import typing

from .base import BaseCorrelationContext

_local_async_storage = contextvars.ContextVar("eave_corr_ctx")


class AsyncioCorrelationContext(BaseCorrelationContext):
    def _get_storage(self) -> dict[str, typing.Any]:
        eave_ctx = contextvars.copy_context().get(_local_async_storage, None)
        if not eave_ctx:
            _local_async_storage.set({"context": {}})
            # refetch ctx vars now that we've set a value
            eave_ctx = contextvars.copy_context().get(_local_async_storage)
        return typing.cast(dict[str, typing.Any], eave_ctx)

    def get(self, key: str) -> typing.Any:
        storage = self._get_storage()
        return storage.get(key, None) or storage.get("context", {}).get(key, None)

    def set(self, key: str, value: typing.Any) -> None:
        storage = self._get_storage()
        storage["context"][key] = value

    def to_json(self) -> str:
        storage = self._get_storage()
        return json.dumps(storage)
