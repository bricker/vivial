import asyncio
import atexit
import multiprocessing
import time
from dataclasses import dataclass
from queue import Empty

from . import config
from .datastructures import EventPayload, EventType
from .ingest_api import send_batch
from .logging import EAVE_LOGGER


@dataclass
class QueueParams:
    event_type: EventType
    # We use this instead of the Queue `maxsize` parameter so that `put` never blocks or fails
    maxsize: int
    maxage_seconds: int

    def __init__(self, event_type: EventType, maxsize: int | None = None, maxage_seconds: int | None = None) -> None:
        self.event_type = event_type
        self.maxsize = maxsize if maxsize is not None else config.batch_maxsize()
        self.maxage_seconds = maxage_seconds if maxage_seconds is not None else config.batch_maxage_seconds()


# TODO: sigterm handler
async def _process_queue(q: multiprocessing.Queue, params: QueueParams) -> None:
    buffer: list[str] = []
    lastflush = time.time()

    while True:
        try:
            payload = q.get(block=True, timeout=params.maxage_seconds)
            if payload:
                buffer.append(payload)
        except Empty:
            pass

        buflen = len(buffer)
        if buflen == 0:
            continue

        now = time.time()

        if buflen >= params.maxsize or now - lastflush >= params.maxage_seconds:
            buffer_copy = buffer.copy()

            try:
                await send_batch(event_type=params.event_type, events=buffer_copy)
            except Exception as e:
                EAVE_LOGGER.exception(e)
            else:
                buffer.clear()
                lastflush = now


def _queue_processor_event_loop(*args, **kwargs) -> None:
    asyncio.run(_process_queue(*args, **kwargs))


class BatchWriteQueue:
    _queue: multiprocessing.Queue
    _process: multiprocessing.Process

    def __init__(self, queue_params: QueueParams) -> None:
        self._queue = multiprocessing.Queue()
        self._process = multiprocessing.Process(
            target=_queue_processor_event_loop,
            kwargs={
                "q": self._queue,
                "params": queue_params,
            },
        )

    def __del__(self) -> None:
        """Cleanup dangling processes before garbage collection completes"""
        if getattr(self, "_queue", None) and getattr(self, "_process", None):
            self.start_autoflush()

    def start_autoflush(self) -> None:
        atexit.register(self.stop_autoflush)
        self._process.start()

    def stop_autoflush(self) -> None:
        # FIXME: Why do we need this? Without it, `q.get()` in the processor has the mutex and `process.terminate()` never resolves. But there must be a better way.
        self._queue.cancel_join_thread()
        self._process.terminate()

        try:
            buffer = []
            while not self._queue.empty():
                buffer.append(self._queue.get(block=False))
            print("FIXME: on close, buffer should be flushed and sent to the server", buffer)
        except Exception as e:
            EAVE_LOGGER.exception(e)

    def put(self, payload: EventPayload) -> None:
        if self._process.is_alive():
            self._queue.put(payload.to_json(), block=False)
        else:
            EAVE_LOGGER.warning("Queue processor is not alive; queueing failed.")
