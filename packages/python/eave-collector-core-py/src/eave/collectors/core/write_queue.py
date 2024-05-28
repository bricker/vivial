import abc
import asyncio
import atexit
import multiprocessing
import multiprocessing.synchronize
import sys
import time
from dataclasses import dataclass
from queue import Empty

from . import config
from .datastructures import EventPayload
from .ingest_api import send_batch
from .json import JsonObject
from .logging import EAVE_LOGGER

_FAILSAFE_MAX_FAILURES = 10


class QueueParams:
    # We use this instead of the Queue `maxsize` parameter so that `put` never blocks or fails
    maxsize: int
    flush_frequency_seconds: int

    def __init__(self, *, maxsize: int | None = None, flush_frequency_seconds: int | None = None) -> None:
        # Ensure > 0
        self.maxsize = max(maxsize if maxsize is not None else config.queue_maxsize(), 1)

        # Ensure not negative
        self.flush_frequency_seconds = max(
            flush_frequency_seconds if flush_frequency_seconds is not None else config.queue_flush_frequency_seconds(),
            0,
        )


@dataclass
class QueueItem:
    event_type: str
    payload: str


# TODO: sigterm handler
async def _process_queue(
    q: multiprocessing.Queue, params: QueueParams, queue_closed_event: multiprocessing.synchronize.Event
) -> int:
    EAVE_LOGGER.info("Eave queue processor started.")

    buffer: dict[str, list[JsonObject]] = {}
    buflen = 0
    last_flush = time.time()
    force_flush = False
    failsafe_counter = 0

    while True:
        queue_closed = queue_closed_event.is_set()
        try:
            # If the queue has been closed by the controlling process, then don't block, so that the queue is flushed as quickly as possible.
            payload = q.get(block=(not queue_closed), timeout=params.flush_frequency_seconds)

            if isinstance(payload, tuple) and len(payload) == 2:
                event_type: str
                event_json: JsonObject
                event_type, event_json = payload

                buffer.setdefault(event_type, [])
                buffer[event_type].append(event_json)
                buflen += 1
            else:
                EAVE_LOGGER.error("Invalid payload type")
                failsafe_counter += 1
        except Empty:
            # The queue is empty. If the queue has been closed by the controlling process, then do a final flush.
            if queue_closed:
                force_flush = True
        except Exception as e:
            # This may indicate a problem with the buffer.
            EAVE_LOGGER.exception(e)
            failsafe_counter += 1

        now = time.time()

        if buflen > 0 and (
            force_flush or buflen >= params.maxsize or now - last_flush >= params.flush_frequency_seconds
        ):
            try:
                EAVE_LOGGER.debug("Sending event batch to Eave.")
                await send_batch(events=buffer)
                buffer.clear()
                buflen = 0
                failsafe_counter = 0
                last_flush = now
            except Exception as e:
                # Probably a failed network request.
                EAVE_LOGGER.exception(e)
                failsafe_counter += 1

        if failsafe_counter >= _FAILSAFE_MAX_FAILURES:
            EAVE_LOGGER.error("Queue processor failsafe threshold reached! Terminating.")
            return 1

        if buflen == 0 and queue_closed:
            # The queue was closed and has been completely flushed. The queue processor can be ended.
            EAVE_LOGGER.info("Queue processor complete. Terminating.")
            return 0


def _queue_processor_event_loop(*args, **kwargs) -> None:
    result = asyncio.run(_process_queue(*args, **kwargs))
    EAVE_LOGGER.info("Eave queue processor ended.")
    sys.exit(result)


class WriteQueue(abc.ABC):
    @abc.abstractmethod
    def start_autoflush(self) -> None:
        ...

    @abc.abstractmethod
    def stop_autoflush(self) -> None:
        ...

    @abc.abstractmethod
    def put(self, payload: EventPayload) -> None:
        ...


class BatchWriteQueue(WriteQueue):
    _queue: multiprocessing.Queue
    _queue_closed_event: multiprocessing.synchronize.Event
    _process: multiprocessing.Process

    def __init__(self, queue_params: QueueParams | None = None) -> None:
        queue_params = queue_params or QueueParams()

        self._queue = multiprocessing.Queue()
        self._queue_closed_event = multiprocessing.Event()
        self._process = multiprocessing.Process(
            target=_queue_processor_event_loop,
            kwargs={
                "q": self._queue,
                "params": queue_params,
                "queue_closed_event": self._queue_closed_event,
            },
        )

    def start_autoflush(self) -> None:
        try:
            atexit.register(self.stop_autoflush)
            self._process.start()
        except Exception as e:
            EAVE_LOGGER.exception(e)
            atexit.unregister(self.stop_autoflush)

    def stop_autoflush(self) -> None:
        try:
            if self._process.is_alive():
                self._queue_closed_event.set()
                EAVE_LOGGER.info("Waiting for queue processor to finish (timeout=10s)...")
                self._process.join(timeout=10)
        except Exception as e:
            EAVE_LOGGER.exception(e)

    def put(self, payload: EventPayload) -> None:
        try:
            if self._process.is_alive() and not self._queue_closed_event.is_set():
                item = (str(payload.event_type), payload.to_dict())
                self._queue.put(item, block=False)
            else:
                EAVE_LOGGER.warning("Queue processor is not alive; queueing failed.")
        except Exception as e:
            EAVE_LOGGER.exception(e)
