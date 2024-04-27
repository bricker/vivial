from eave.collectors.core.datastructures import EventType
from eave.collectors.core.write_queue import BatchWriteQueue, QueueParams


class BaseCollector:
    _event_type: EventType
    enabled: bool = False
    write_queue: BatchWriteQueue

    def __init__(self, event_type: EventType) -> None:
        self._event_type = event_type
        self.write_queue = BatchWriteQueue(queue_params=QueueParams(event_type=event_type))

    def start_base(self) -> None:
        if not self.enabled:
            self.write_queue.start_autoflush()
            self.enabled = True

    def stop_base(self) -> None:
        if self.enabled:
            self.enabled = False
            self.write_queue.stop_autoflush()
