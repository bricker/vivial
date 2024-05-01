from eave.collectors.starlette.private.collector import StarletteCollector

_collector: StarletteCollector | None = None


class StarletteCollectorManager:
    @classmethod
    def start(cls) -> None:
        global _collector

        if not _collector:
            _collector = StarletteCollector()
            _collector.instrument()

    @classmethod
    def stop(cls) -> None:
        global _collector

        if _collector:
            _collector.uninstrument()

        _collector = None

    @classmethod
    def instrumentation_dependencies(cls) -> list[str]:
        return ["starlette"]
