import asyncio
import atexit
from dataclasses import dataclass
import multiprocessing
from queue import Empty
import time

from .ingestion_api import send_data

from .datastructures import EventType


@dataclass
class QueueParams:
    event_type: EventType
    maxsize: int = 0  # We use this instead of the Queue `maxsize` parameter so that `put` never blocks or fails
    maxage_seconds: int = 30


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
            print("Flushing...", flush=True)
            buffer_copy = buffer.copy()

            try:
                await send_data(event_type=params.event_type, events=buffer_copy)
            except Exception as e:
                print(e)
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
            print(e)

    def put(self, payload: str) -> None:
        self._queue.put(payload, block=False)
