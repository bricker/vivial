from eave.collectors.core.agent import SHARED_BATCH_WRITE_QUEUE, Agent


class BaseCollector:
    enabled: bool = False
    write_queue: Agent

    def __init__(self, *, write_queue: Agent = SHARED_BATCH_WRITE_QUEUE) -> None:
        self.write_queue = write_queue

    def run(self) -> None:
        if not self.enabled:
            self.write_queue.start()
            self.enabled = True

    def terminate(self) -> None:
        if self.enabled:
            self.enabled = False
            self.write_queue.stop()
