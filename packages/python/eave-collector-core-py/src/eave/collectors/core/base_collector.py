from eave.collectors.core.write_queue import BatchWriteQueue, WriteQueue


class BaseCollector:
    enabled: bool = False
    write_queue: WriteQueue

    def __init__(self, *, write_queue: WriteQueue | None = None) -> None:
        self.write_queue = write_queue or BatchWriteQueue()

    def run(self) -> None:
        if not self.enabled:
            self.write_queue.start_autoflush()
            self.enabled = True

    def terminate(self) -> None:
        if self.enabled:
            self.enabled = False
            self.write_queue.stop_autoflush()
