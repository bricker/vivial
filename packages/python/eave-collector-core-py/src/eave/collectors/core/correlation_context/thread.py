import threading

from .base import STORAGE_ATTR, BaseCorrelationContext, CorrCtxStorage

# TODO: customer child threads wont share this storage
_local_thread_storage = threading.local()


class ThreadedCorrelationContext(BaseCorrelationContext):
    def init_storage(self) -> None:
        setattr(_local_thread_storage, STORAGE_ATTR, CorrCtxStorage())

    def get_storage(self) -> CorrCtxStorage | None:
        if not hasattr(_local_thread_storage, STORAGE_ATTR):
            self.init_storage()

        return getattr(_local_thread_storage, STORAGE_ATTR, None)
