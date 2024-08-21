import abc
import asyncio
import atexit
import queue
import time
import logging
from queue import Empty
from threading import Lock, Thread

from eave.collectors.core.agent.data_handler import DataHandler
from eave.collectors.core import config
from eave.collectors.core.datastructures import Batchable

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


class Agent(abc.ABC):
    @abc.abstractmethod
    def start(self) -> None: ...

    @abc.abstractmethod
    def stop(self) -> None: ...

    @abc.abstractmethod
    def put(self, payload: Batchable) -> None: ...


class EaveAgent(Agent):
    _queue_params: QueueParams
    _queue: queue.Queue
    _lock: Lock
    _thread: Thread | None = None
    _logger: logging.Logger
    _data_handler: DataHandler

    def __init__(self, logger: logging.Logger, data_handler: DataHandler, queue_params: QueueParams | None = None) -> None:
        self._queue = queue.Queue(maxsize=0) # Infinite queue size.
        self._queue_params = queue_params or QueueParams()
        self._lock = Lock()
        self._logger = logger
        self._data_handler = data_handler

    def is_alive(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        with self._lock:
            if self.is_alive():
                return

            self._thread = Thread(target=self._worker_event_loop, name="eave-agent", daemon=True)
            self._thread.start()
            atexit.register(self.stop)

    def stop(self) -> None:
        if not self.is_alive():
            return

        # For the typechecker
        assert self._thread is not None

        with self._lock:
            self._queue.put(_QUEUE_CLOSED_SENTINEL, block=False)
            self._thread.join(timeout=10)
            self._thread = None

    def put(self, payload: Batchable) -> None:
        try:
            self._queue.put(payload, block=False)
        except queue.Full as e:
            # This won't be raised if the max queue size is infinite, but I'm leaving it here
            # in case we decide later to put a max queue size.
            self._logger.exception(e)
        except Exception as e:
            self._logger.exception(e)


    def _worker_event_loop(self, *args, **kwargs) -> None:
        try:
            asyncio.run(self._worker(*args, **kwargs))
        except KeyboardInterrupt:
            pass
        except TooManyFailuresError as e:
            self._logger.exception(e)

        self._logger.info("Eave agent ended.")

    async def _worker(self) -> None:
        self._logger.info("Eave agent started.")

        buffer: list[Batchable] = []
        last_flush = time.time()
        failsafe_counter = 0
        queue_closed = False

        while True:
            force_flush = False

            try:
                elapsed = time.time() - last_flush
                timeout = max(0, self._queue_params.flush_frequency_seconds - elapsed)
                # If the queue has been closed by the controlling process, then don't block, so that the queue is flushed as quickly as possible.
                payload = self._queue.get(block=(not queue_closed), timeout=timeout)
                self._queue.task_done()

                if self._data_handler.validate_data_type(payload):
                    buffer.append(payload)
                elif payload == _QUEUE_CLOSED_SENTINEL:
                    # By setting this, the queue will now be processed as quickly as possible.
                    # We'll no longer wait for an item to be placed on the queue; we'll instead
                    # process the queue immediately until an `Empty` exception is raised, and then force-flush
                    # and end the process.
                    queue_closed = True
                else:
                    self._logger.error("Invalid payload type")
                    failsafe_counter += 1
            except Empty:
                # The queue is empty. If the queue has been closed by the controlling process, then do a final flush.
                if queue_closed:
                    force_flush = True
            except Exception as e:
                # This may indicate a problem with the buffer.
                self._logger.exception(e)
                failsafe_counter += 1

            now = time.time()

            buflen = len(buffer)
            if buflen > 0 and (
                force_flush or buflen >= self._queue_params.maxsize or now - last_flush >= self._queue_params.flush_frequency_seconds
            ):
                try:
                    self._logger.debug(
                        "Sending data batch to Eave. buflen=%d, last_flush=%s, force_flush=%s, failsafe_counter=%d",
                        buflen,
                        str(last_flush),
                        str(force_flush),
                        failsafe_counter,
                    )

                    await self._data_handler.send_buffer(buffer)
                    buffer.clear()
                    buflen = 0
                    failsafe_counter = 0
                    last_flush = now
                except Exception as e:
                    # Probably a failed network request.
                    self._logger.exception(e)
                    failsafe_counter += 1

            if failsafe_counter >= _FAILSAFE_MAX_FAILURES:
                raise TooManyFailuresError("Eave agent failsafe threshold reached! Terminating.")

            if buflen == 0 and queue_closed:
                # The queue was closed and has been completely flushed. The queue processor can be ended.
                self._logger.info("Eave agent complete. Terminating.")
                break
