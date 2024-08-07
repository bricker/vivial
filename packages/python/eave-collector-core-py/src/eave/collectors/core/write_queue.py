import abc
import asyncio
import atexit
import multiprocessing
import multiprocessing.queues
import multiprocessing.synchronize
import queue
import sys
import time
from dataclasses import dataclass
from multiprocessing.context import SpawnProcess
from queue import Empty
from threading import Lock

from . import config
from .datastructures import EventPayload
from .ingest_api import send_batch
from .json import JsonObject
from .logging import EAVE_LOGGER

_FAILSAFE_MAX_FAILURES = 10
_QUEUE_CLOSED_SENTINEL = "QUEUE_CLOSED_SENTINEL"


class TooManyFailuresError(Exception):
    pass


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


async def _process_queue(
    q: multiprocessing.Queue,
    params: QueueParams,
) -> int:
    EAVE_LOGGER.info("Eave queue processor started.")

    buffer: dict[str, list[JsonObject]] = {}
    buflen = 0
    last_flush = time.time()
    force_flush = False
    failsafe_counter = 0
    queue_closed = False

    while True:
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
            elif payload == _QUEUE_CLOSED_SENTINEL:
                # By setting this, the queue will now be processed as quickly as possible.
                # We'll no longer wait for an item to be placed on the queue; we'll instead
                # process the queue immediately until an `Empty` exception is raised, and then force-flush
                # and end the process.
                queue_closed = True
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
                EAVE_LOGGER.debug(
                    "Sending event batch to Eave. buflen=%d, last_flush=%s, force_flush=%s, failsafe_counter=%d",
                    buflen,
                    str(last_flush),
                    str(force_flush),
                    failsafe_counter,
                )
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
            raise TooManyFailuresError("Queue processor failsafe threshold reached! Terminating.")

        if buflen == 0 and queue_closed:
            # The queue was closed and has been completely flushed. The queue processor can be ended.
            EAVE_LOGGER.info("Queue processor complete. Terminating.")
            return 0


def _queue_processor_event_loop(*args, **kwargs) -> None:
    try:
        result = asyncio.run(_process_queue(*args, **kwargs))
    except KeyboardInterrupt:
        result = 0
    except TooManyFailuresError as e:
        EAVE_LOGGER.exception(e)
        result = 2

    EAVE_LOGGER.info("Eave queue processor ended.")
    sys.exit(result)


class WriteQueue(abc.ABC):
    @abc.abstractmethod
    def start_autoflush(self) -> None: ...

    @abc.abstractmethod
    def stop_autoflush(self) -> None: ...

    @abc.abstractmethod
    def put(self, payload: EventPayload) -> None: ...


_spawn = multiprocessing.get_context("spawn")


class BatchWriteQueue(WriteQueue):
    _queue_params: QueueParams
    _queue: multiprocessing.queues.Queue | None = None
    _process: SpawnProcess | None = None
    _lock: Lock

    def __init__(self, queue_params: QueueParams | None = None) -> None:
        self._queue_params = queue_params or QueueParams()
        self._lock = Lock()

    def start_autoflush(self) -> None:
        if self._process and self._process.is_alive():
            return

        if self._lock.acquire(blocking=False):
            try:
                self._queue = _spawn.Queue()
                self._process = _spawn.Process(
                    name="eave-agent",
                    target=_queue_processor_event_loop,
                    daemon=True,
                    kwargs={
                        "q": self._queue,
                        "params": self._queue_params,
                    },
                )

                atexit.register(self.stop_autoflush)
                self._process.start()
            except Exception as e:
                EAVE_LOGGER.exception(e)
                atexit.unregister(self.stop_autoflush)
            finally:
                self._lock.release()

    def stop_autoflush(self) -> None:
        if not self._process or not self._process.is_alive():
            return

        if self._lock.acquire(blocking=False):
            try:
                EAVE_LOGGER.info("Waiting for queue processor to finish (timeout=10s)...")
                if self._queue:
                    self._queue.put(_QUEUE_CLOSED_SENTINEL, block=True, timeout=10)
            except queue.Full:
                # Forcefully kill the process if the queue couldn't be closed after 10 seconds.
                self._process.terminate()
            except Exception as e:
                EAVE_LOGGER.exception(e)
            finally:
                if self._queue:
                    self._queue.close()

                self._queue = None
                self._process.join(timeout=10)
                self._process.close()
                self._process = None
                self._lock.release()

    def put(self, payload: EventPayload) -> None:
        try:
            if self._queue:
                item = (str(payload.event_type), payload.to_dict())
                self._queue.put(item, block=False)
            else:
                EAVE_LOGGER.warning("Queue processor is not alive; queueing failed.")
        except queue.Full as e:
            EAVE_LOGGER.exception(e)
        except Exception as e:
            EAVE_LOGGER.exception(e)


SHARED_BATCH_WRITE_QUEUE = BatchWriteQueue()
