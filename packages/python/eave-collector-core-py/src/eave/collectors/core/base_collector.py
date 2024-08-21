from eave.collectors.core.agent.atom_agent import SHARED_BATCHED_ATOM_WRITE_QUEUE
from eave.collectors.core.agent import Agent


class BaseCollector:
    enabled: bool = False
    write_queue: Agent

    def __init__(self, *, write_queue: Agent = SHARED_BATCHED_ATOM_WRITE_QUEUE) -> None:
        self.write_queue = write_queue

    def run(self) -> None:
        if not self.enabled:
            self.write_queue.start()
            self.enabled = True

    def terminate(self) -> None:
        if self.enabled:
            self.enabled = False
            self.write_queue.stop()
