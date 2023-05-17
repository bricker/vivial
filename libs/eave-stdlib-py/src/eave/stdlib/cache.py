import abc
from dataclasses import dataclass
from datetime import datetime
import time
from typing import Any, Optional, Protocol
import redis.asyncio as redis
from .config import shared_config

class _Cache(Protocol):
    @abc.abstractmethod
    async def get(self, name: str) -> str | None:
        ...

    @abc.abstractmethod
    async def set(self, name: str, value: str, ex: Optional[int] = None) -> bool | None:
        ...

    @abc.abstractmethod
    async def delete(self, *names: str) -> int:
        ...

class _CacheEntry:
    value: str
    ts: float
    ex: Optional[int] = None

    def __init__(self, value: str, ex: Optional[int] = None) -> None:
        self.value = value
        self.ex = ex
        self.ts = time.time()

    @property
    def expired(self) -> bool:
        return self.ex is not None and (self.ts + self.ex < time.time())

class EphemeralCache(_Cache):
    _store: dict[str,_CacheEntry] = {}

    async def get(self, name: str) -> str | None:
        e = self._store.get(name)
        if e is None:
            return None
        elif e.expired:
            await self.delete(name)
            return None
        else:
            return e.value

    async def set(self, name: str, value: str, ex: Optional[int] = None) -> bool | None:
        # quick way to put a hard limit on the size of this cache.
        # This class is only for development so there's no need for anything more complex than this.
        if len(self._store.keys()) > 100:
            self._store.clear()

        self._store[name] = _CacheEntry(value=value, ex=ex)
        return True

    async def delete(self, *names: str) -> int:
        num = 0
        for k in names:
            try:
                self._store.pop(k)
                num += 1
            except KeyError:
                pass

        return num

impl: _Cache

if redis_cfg := shared_config.redis_connection:
    host, port, db = redis_cfg
    auth = shared_config.redis_auth
    impl = redis.Redis(host=host, port=port, db=db, password=auth, decode_responses=True)
else:
    impl = EphemeralCache()

async def set(name: str, value: str, ex: Optional[int] = None) -> bool | None:
    success = await impl.set(name, value, ex=ex)
    return success

async def get(name: str) -> str | None:
    value = await impl.get(name)
    if value is not None:
        return str(value)
    else:
        return None

async def delete(*names: str) -> int:
    num = await impl.delete(*names)
    return num
