from django_orm.private.collector import DjangoOrmCollector

_collector: DjangoOrmCollector | None = None


class DjangoOrmCollectorManager:
    @classmethod
    def start(cls) -> None:
        global _collector

        if not _collector:
            _collector = DjangoOrmCollector()
            _collector.instrument()

    @classmethod
    def stop(cls) -> None:
        global _collector

        if _collector:
            _collector.uninstrument()

        _collector = None

    @classmethod
    def instrumentation_dependencies(cls) -> list[str]:
        return ["django"]
