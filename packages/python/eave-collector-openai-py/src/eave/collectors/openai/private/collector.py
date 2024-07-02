from eave.collectors.core.base_ai_collector import BaseAICollector
from eave.collectors.core.write_queue import WriteQueue


class OpenAICollector(BaseAICollector):
    def __init__(self, *, write_queue: WriteQueue | None = None) -> None:
        super().__init__(write_queue=write_queue)
