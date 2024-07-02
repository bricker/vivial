from eave.collectors.openai.private.collector import OpenAICollector

_collector: OpenAICollector | None = None


class OpenAICollectorManager:
    @classmethod
    def start(cls) -> None:
        global _collector

        if not _collector:
            _collector = OpenAICollector()
            _collector.instrument()

    @classmethod
    def stop(cls) -> None:
        global _collector

        if _collector:
            _collector.uninstrument()

        _collector = None

    @classmethod
    def instrumentation_dependencies(cls) -> list[str]:
        return ["openai"]
