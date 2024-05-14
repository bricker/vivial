from eave.collectors.core.datastructures import EventPayload
from eave.collectors.core.write_queue import WriteQueue


class EphemeralWriteQueue(WriteQueue):
    _running: bool = False
    queue: list[EventPayload]

    def __init__(self) -> None:
        self.queue = []

    def start_autoflush(self) -> None:
        self._running = True

    def stop_autoflush(self) -> None:
        self._running = False

    def put(self, payload: EventPayload) -> None:
        if not self._running:
            raise RuntimeError("queue processor not running")

        self.queue.append(payload)
