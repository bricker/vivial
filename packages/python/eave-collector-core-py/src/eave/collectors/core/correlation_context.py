import abc
import contextvars
import json
import threading
import typing


class BaseCorrelationContext(abc.ABC):
    @abc.abstractmethod
    def get(self, key: str) -> typing.Any: ...

    @abc.abstractmethod
    def set(self, key: str, value: typing.Any) -> None: ...

    @abc.abstractmethod
    def to_json(self) -> str: ...


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


# TODO: figure out which ctx storage type we need at runtime?
corr_ctx = ThreadedCorrelationContext()
