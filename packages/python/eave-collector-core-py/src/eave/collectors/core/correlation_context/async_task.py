import contextvars

from .base import STORAGE_ATTR, BaseCorrelationContext, CorrCtxStorage

_local_async_storage = contextvars.ContextVar[CorrCtxStorage](STORAGE_ATTR)


class AsyncioCorrelationContext(BaseCorrelationContext):
    def init_storage(self) -> None:
        _local_async_storage.set(CorrCtxStorage())

    def get_storage(self) -> CorrCtxStorage | None:
        eave_ctx = _local_async_storage.get(None)
        if not eave_ctx:
            self.init_storage()

        return _local_async_storage.get(None)
