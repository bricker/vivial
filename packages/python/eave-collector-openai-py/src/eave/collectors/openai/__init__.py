from eave.collectors.openai.private.collector import OpenAICollector
from openai import AsyncOpenAI, OpenAI

_collector: OpenAICollector | None = None


class OpenAICollectorManager:
    @classmethod
    def start(cls, client: OpenAI | AsyncOpenAI | None = None) -> None:
        global _collector

        if not _collector:
            _collector = OpenAICollector()
            _collector.instrument(client=client)

    @classmethod
    def stop(cls) -> None:
        global _collector

        if _collector:
            _collector.uninstrument()

        _collector = None

    @classmethod
    def instrumentation_dependencies(cls) -> list[str]:
        return ["openai"]
