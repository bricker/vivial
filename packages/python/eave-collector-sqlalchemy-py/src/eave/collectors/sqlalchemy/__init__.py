from eave.collectors.sqlalchemy.private.collector import SQLAlchemyCollector, SupportedEngine

_collector: SQLAlchemyCollector | None = None


class SQLAlchemyCollectorManager:
    @classmethod
    def start(cls, engine: SupportedEngine) -> None:
        global _collector

        if not _collector:
            _collector = SQLAlchemyCollector()
            _collector.start(engine)

    @classmethod
    def stop(cls) -> None:
        global _collector

        if _collector:
            _collector.stop()

        _collector = None  # Deallocate the engine.
