import asyncio
import atexit
import multiprocessing
from multiprocessing.connection import Connection
import sys
from typing import Any
from eave.stdlib.task_queue import do_in_background

from .datastructures import RawEvent
from . import clickhouse

# We use this instead of the Queue `maxsize` parameter so that `put` never blocks or fails
_buffer_maxsize = 100

def _process_queue(q: multiprocessing.Queue) -> None:
    buffer = []
    while True:
        e = q.get()
        buffer.append(e)
        if len(buffer) >= _buffer_maxsize:
            buffer_copy = buffer.copy()
            buffer.clear()
            clickhouse.insert(buffer_copy)

class BatchWriteQueue:
    _queue: multiprocessing.Queue
    _process: multiprocessing.Process

    def __init__(self) -> None:
        self._queue = multiprocessing.Queue()
        self._process = multiprocessing.Process(
            target=_process_queue,
            kwargs={
                "q": self._queue,
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

            # FIXME: "Unrecognized column 'team_id' in table raw_events" ?
            clickhouse.insert(buffer)
            print("insert complete")
        except Exception as e:
            print(e)

    def put(self, event: RawEvent) -> None:
        # print(">>> PUT", event)
        self._queue.put_nowait(event)

write_queue = BatchWriteQueue()
