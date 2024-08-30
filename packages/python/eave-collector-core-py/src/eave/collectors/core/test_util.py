from eave.collectors.core.agent import Agent
from eave.collectors.core.datastructures import Batchable


class EphemeralWriteQueue(Agent):
    _running: bool = False
    queue: list[Batchable]

    def __init__(self) -> None:
        self.queue = []

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def put(self, payload: Batchable) -> None:
        if not self._running:
            raise RuntimeError("queue processor not running")

        self.queue.append(payload)
