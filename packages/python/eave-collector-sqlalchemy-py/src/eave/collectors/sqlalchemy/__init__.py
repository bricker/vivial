from eave.collectors.sqlalchemy.private.collector import SQLAlchemyCollector, SupportedEngine

_collector: SQLAlchemyCollector | None = None


async def start_eave_sqlalchemy_collector(engine: SupportedEngine, credentials: str | None = None) -> None:
    global _collector

    if not _collector:
        _collector = SQLAlchemyCollector(credentials=credentials)
        await _collector.start(engine)


def stop_eave_sqlalchemy_collector() -> None:
    global _collector

    if _collector:
        _collector.stop()

    _collector = None  # Deallocate the engine.
