import contextvars

from .base import STORAGE_ATTR, BaseCorrelationContext, CorrCtxStorage

_local_async_storage = contextvars.ContextVar[CorrCtxStorage](STORAGE_ATTR)


class AsyncioCorrelationContext(BaseCorrelationContext):
    def init_storage(self) -> None:
        _local_async_storage.set(CorrCtxStorage())

    def get_storage(self) -> CorrCtxStorage | None:
        current_context = contextvars.copy_context()
        eave_ctx = current_context.get(_local_async_storage)
        if not eave_ctx:
            self.init_storage()

        return current_context.get(_local_async_storage)
