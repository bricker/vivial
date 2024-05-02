from eave.collectors.starlette.private.collector import StarletteCollector
from starlette.applications import Starlette

_collector: StarletteCollector | None = None


class StarletteCollectorManager:
    @classmethod
    def start(cls, app: Starlette | None) -> None:
        global _collector

        if not _collector:
            _collector = StarletteCollector()
            if app is not None:
                _collector.instrument_app(app=app)
            else:
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
