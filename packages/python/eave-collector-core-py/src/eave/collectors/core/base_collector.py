from eave.collectors.core.write_queue import SHARED_BATCH_WRITE_QUEUE, WriteQueue


class BaseCollector:
    enabled: bool = False
    write_queue: WriteQueue

    def __init__(self, *, write_queue: WriteQueue = SHARED_BATCH_WRITE_QUEUE) -> None:
        self.write_queue = write_queue

    def run(self) -> None:
        if not self.enabled:
            self.write_queue.start_autoflush()
            self.enabled = True

    def terminate(self) -> None:
        if self.enabled:
            self.enabled = False
            self.write_queue.stop_autoflush()
