from eave.collectors.core.datastructures import EventPayload, EventType
from eave.collectors.core.write_queue import BatchWriteQueue, QueueParams


class ConsoleOutputBatchWriteQueue(BatchWriteQueue):
    _running: bool = False
    queue: list[EventPayload]

    def __init__(self, event_type: EventType) -> None:
        super().__init__(queue_params=QueueParams(event_type=event_type))
        self.queue = []

    def start_autoflush(self) -> None:
        self._running = True

    def stop_autoflush(self) -> None:
        self._running = False

    def put(self, payload: EventPayload) -> None:
        if not self._running:
            raise RuntimeError("queue processor not running")

        self.queue.append(payload)
