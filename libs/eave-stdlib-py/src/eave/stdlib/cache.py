import abc
import time
from typing import Protocol, override


class CacheInterface(Protocol):
    @abc.abstractmethod
    async def get(self, name: str) -> str | None: ...

    @abc.abstractmethod
    async def set(self, name: str, value: str, ex: int | None = None) -> bool | None: ...

    @abc.abstractmethod
    async def delete(self, *names: str) -> int: ...

    @abc.abstractmethod
    async def close(self, close_connection_pool: bool | None = None) -> None: ...

    @abc.abstractmethod
    async def ping(self) -> bool: ...


class _CacheEntry:
    value: str
    ts: float
    ex: int | None = None

    def __init__(self, value: str, ex: int | None = None) -> None:
        self.value = value
        self.ex = ex
        self.ts = time.time()

    @property
    def expired(self) -> bool:
        return self.ex is not None and (self.ts + self.ex < time.time())


class EphemeralCache(CacheInterface):
    _store: dict[str, _CacheEntry]

    def __init__(self) -> None:
        self._store = {}

    @override
    async def get(self, name: str) -> str | None:
        e = self._store.get(name)
        if e is None:
            return None
        elif e.expired:
            await self.delete(name)
            return None
        else:
            return e.value

    @override
    async def set(self, name: str, value: str, ex: int | None = None) -> bool | None:
        # quick way to put a hard limit on the size of this cache.
        # This class is only for development so there's no need for anything more complex than this.
        if len(self._store.keys()) > 100:
            self._store.clear()

        self._store[name] = _CacheEntry(value=value, ex=ex)
        return True

    @override
    async def delete(self, *names: str) -> int:
        num = 0
        for k in names:
            try:
                self._store.pop(k)
                num += 1
            except KeyError:
                pass

        return num

    @override
    async def close(self, close_connection_pool: bool | None = None) -> None:
        return None

    @override
    async def ping(self) -> bool:
        return True
