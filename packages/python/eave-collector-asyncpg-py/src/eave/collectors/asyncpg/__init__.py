from typing import Any

from eave.collectors.asyncpg.private.collector import AsyncpgCollector

__collector: AsyncpgCollector | None = None

async def start_eave_asyncpg_collector(*args: Any, **kwargs: Any) -> None:
    # TODO: The args and kwargs are pass-through to asyncpg.connect(). They need some kind of documentation.
    global __collector

    if not __collector:
        __collector = AsyncpgCollector(*args, **kwargs)
        await __collector.start()

async def stop_eave_asyncpg_collector() -> None:
    global __collector

    if __collector:
        await __collector.stop()

    __collector = None # Deallocate the engine.
