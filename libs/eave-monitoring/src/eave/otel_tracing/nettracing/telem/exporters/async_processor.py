import collections
import logging
import os
import sys
import threading
import typing
from enum import Enum
from os import environ, linesep
from time import time_ns
from typing import Optional
from opentelemetry.sdk.trace import SpanProcessor, Span, ReadableSpan
from opentelemetry.context import Context

from .async_exporter import AsyncSpanExporter

_DEFAULT_SCHEDULE_DELAY_MILLIS = 5000
_DEFAULT_MAX_EXPORT_BATCH_SIZE = 512
_DEFAULT_EXPORT_TIMEOUT_MILLIS = 30000
_DEFAULT_MAX_QUEUE_SIZE = 2048
_ENV_VAR_INT_VALUE_ERROR_MESSAGE = (
    "Unable to parse value for %s as integer. Defaulting to %s."
)
logger = logging.getLogger(__name__)


class AsyncBatchSpanProcessor(SpanProcessor):
    """Batch span processor implementation.

    `AsyncBatchSpanProcessor` is an implementation of `SpanProcessor` that
    batches ended spans and pushes them to the configured `SpanExporter`.

    `AsyncBatchSpanProcessor` is configurable with the following environment
    variables which correspond to constructor parameters:

    - :envvar:`OTEL_BSP_SCHEDULE_DELAY`
    - :envvar:`OTEL_BSP_MAX_QUEUE_SIZE`
    - :envvar:`OTEL_BSP_MAX_EXPORT_BATCH_SIZE`
    - :envvar:`OTEL_BSP_EXPORT_TIMEOUT`
    """

    def __init__(
        self,
        span_exporter: AsyncSpanExporter,
        max_queue_size: int|None = None,
        schedule_delay_millis: float|None = None,
        max_export_batch_size: int|None = None,
        export_timeout_millis: float|None = None,
    ):
        if max_queue_size is None:
            max_queue_size = AsyncBatchSpanProcessor._default_max_queue_size()

        if schedule_delay_millis is None:
            schedule_delay_millis = (
                AsyncBatchSpanProcessor._default_schedule_delay_millis()
            )

        if max_export_batch_size is None:
            max_export_batch_size = (
                AsyncBatchSpanProcessor._default_max_export_batch_size()
            )

        if export_timeout_millis is None:
            export_timeout_millis = (
                AsyncBatchSpanProcessor._default_export_timeout_millis()
            )

        AsyncBatchSpanProcessor._validate_arguments(
            max_queue_size, schedule_delay_millis, max_export_batch_size
        )

        self.span_exporter = span_exporter
        self.queue = collections.deque(
            [], max_queue_size
        )  # type: typing.Deque[Span]
        self.worker_thread = threading.Thread(
            name="OtelAsyncBatchSpanProcessor", target=self.worker, daemon=True
        )
        self.condition = threading.Condition(threading.Lock())
        self._flush_request = None  # type: typing.Optional[_FlushRequest]
        self.schedule_delay_millis = schedule_delay_millis
        self.max_export_batch_size = max_export_batch_size
        self.max_queue_size = max_queue_size
        self.export_timeout_millis = export_timeout_millis
        self.done = False
        # flag that indicates that spans are being dropped
        self._spans_dropped = False
        # precallocated list to send spans to exporter
        self.spans_list = [
            None
        ] * self.max_export_batch_size  # type: typing.List[typing.Optional[Span]]
        self.worker_thread.start()
        if hasattr(os, "register_at_fork"):
            os.register_at_fork(
                after_in_child=self._at_fork_reinit
            )  # pylint: disable=protected-access
        self._pid = os.getpid()

    def on_start(
        self, span: Span, parent_context: typing.Optional[Context] = None
    ) -> None:
        pass

    def on_end(self, span: ReadableSpan) -> None:
        if self.done:
            logger.warning("Already shutdown, dropping span.")
            return
        if not span.context.trace_flags.sampled:
            return
        if self._pid != os.getpid():
            _BSP_RESET_ONCE.do_once(self._at_fork_reinit)

        if len(self.queue) == self.max_queue_size:
            if not self._spans_dropped:
                logger.warning("Queue is full, likely spans will be dropped.")
                self._spans_dropped = True

        self.queue.appendleft(span)

        if len(self.queue) >= self.max_export_batch_size:
            with self.condition:
                self.condition.notify()

    def _at_fork_reinit(self):
        self.condition = threading.Condition(threading.Lock())
        self.queue.clear()

        # worker_thread is local to a process, only the thread that issued fork continues
        # to exist. A new worker thread must be started in child process.
        self.worker_thread = threading.Thread(
            name="OtelAsyncBatchSpanProcessor", target=self.worker, daemon=True
        )
        self.worker_thread.start()
        self._pid = os.getpid()

    def worker(self):
        timeout = self.schedule_delay_millis / 1e3
        flush_request = None  # type: typing.Optional[_FlushRequest]
        while not self.done:
            with self.condition:
                if self.done:
                    # done flag may have changed, avoid waiting
                    break
                flush_request = self._get_and_unset_flush_request()
                if (
                    len(self.queue) < self.max_export_batch_size
                    and flush_request is None
                ):

                    self.condition.wait(timeout)
                    flush_request = self._get_and_unset_flush_request()
                    if not self.queue:
                        # spurious notification, let's wait again, reset timeout
                        timeout = self.schedule_delay_millis / 1e3
                        self._notify_flush_request_finished(flush_request)
                        flush_request = None
                        continue
                    if self.done:
                        # missing spans will be sent when calling flush
                        break

            # subtract the duration of this export call to the next timeout
            start = time_ns()
            self._export(flush_request)
            end = time_ns()
            duration = (end - start) / 1e9
            timeout = self.schedule_delay_millis / 1e3 - duration

            self._notify_flush_request_finished(flush_request)
            flush_request = None

        # there might have been a new flush request while export was running
        # and before the done flag switched to true
        with self.condition:
            shutdown_flush_request = self._get_and_unset_flush_request()

        # be sure that all spans are sent
        self._drain_queue()
        self._notify_flush_request_finished(flush_request)
        self._notify_flush_request_finished(shutdown_flush_request)

    def _get_and_unset_flush_request(
        self,
    ) -> typing.Optional[_FlushRequest]:
        """Returns the current flush request and makes it invisible to the
        worker thread for subsequent calls.
        """
        flush_request = self._flush_request
        self._flush_request = None
        if flush_request is not None:
            flush_request.num_spans = len(self.queue)
        return flush_request

    @staticmethod
    def _notify_flush_request_finished(
        flush_request: typing.Optional[_FlushRequest],
    ):
        """Notifies the flush initiator(s) waiting on the given request/event
        that the flush operation was finished.
        """
        if flush_request is not None:
            flush_request.event.set()

    def _get_or_create_flush_request(self) -> _FlushRequest:
        """Either returns the current active flush event or creates a new one.

        The flush event will be visible and read by the worker thread before an
        export operation starts. Callers of a flush operation may wait on the
        returned event to be notified when the flush/export operation was
        finished.

        This method is not thread-safe, i.e. callers need to take care about
        synchronization/locking.
        """
        if self._flush_request is None:
            self._flush_request = _FlushRequest()
        return self._flush_request

    def _export(self, flush_request: typing.Optional[_FlushRequest]):
        """Exports spans considering the given flush_request.

        In case of a given flush_requests spans are exported in batches until
        the number of exported spans reached or exceeded the number of spans in
        the flush request.
        In no flush_request was given at most max_export_batch_size spans are
        exported.
        """
        if not flush_request:
            self._export_batch()
            return

        num_spans = flush_request.num_spans
        while self.queue:
            num_exported = self._export_batch()
            num_spans -= num_exported

            if num_spans <= 0:
                break

    def _export_batch(self) -> int:
        """Exports at most max_export_batch_size spans and returns the number of
        exported spans.
        """
        idx = 0
        # currently only a single thread acts as consumer, so queue.pop() will
        # not raise an exception
        while idx < self.max_export_batch_size and self.queue:
            self.spans_list[idx] = self.queue.pop()
            idx += 1
        token = attach(set_value(_SUPPRESS_INSTRUMENTATION_KEY, True))
        try:
            # Ignore type b/c the Optional[None]+slicing is too "clever"
            # for mypy
            self.span_exporter.export(self.spans_list[:idx])  # type: ignore
        except Exception:  # pylint: disable=broad-except
            logger.exception("Exception while exporting Span batch.")
        detach(token)

        # clean up list
        for index in range(idx):
            self.spans_list[index] = None
        return idx

    def _drain_queue(self):
        """Export all elements until queue is empty.

        Can only be called from the worker thread context because it invokes
        `export` that is not thread safe.
        """
        while self.queue:
            self._export_batch()

    def force_flush(self, timeout_millis: int = None) -> bool:

        if timeout_millis is None:
            timeout_millis = self.export_timeout_millis

        if self.done:
            logger.warning("Already shutdown, ignoring call to force_flush().")
            return True

        with self.condition:
            flush_request = self._get_or_create_flush_request()
            # signal the worker thread to flush and wait for it to finish
            self.condition.notify_all()

        # wait for token to be processed
        ret = flush_request.event.wait(timeout_millis / 1e3)
        if not ret:
            logger.warning("Timeout was exceeded in force_flush().")
        return ret

    def shutdown(self) -> None:
        # signal the worker thread to finish and then wait for it
        self.done = True
        with self.condition:
            self.condition.notify_all()
        self.worker_thread.join()
        self.span_exporter.shutdown()

    @staticmethod
    def _default_max_queue_size():
        try:
            return int(
                environ.get(OTEL_BSP_MAX_QUEUE_SIZE, _DEFAULT_MAX_QUEUE_SIZE)
            )
        except ValueError:
            logger.exception(
                _ENV_VAR_INT_VALUE_ERROR_MESSAGE,
                OTEL_BSP_MAX_QUEUE_SIZE,
                _DEFAULT_MAX_QUEUE_SIZE,
            )
            return _DEFAULT_MAX_QUEUE_SIZE

    @staticmethod
    def _default_schedule_delay_millis():
        try:
            return int(
                environ.get(
                    OTEL_BSP_SCHEDULE_DELAY, _DEFAULT_SCHEDULE_DELAY_MILLIS
                )
            )
        except ValueError:
            logger.exception(
                _ENV_VAR_INT_VALUE_ERROR_MESSAGE,
                OTEL_BSP_SCHEDULE_DELAY,
                _DEFAULT_SCHEDULE_DELAY_MILLIS,
            )
            return _DEFAULT_SCHEDULE_DELAY_MILLIS

    @staticmethod
    def _default_max_export_batch_size():
        try:
            return int(
                environ.get(
                    OTEL_BSP_MAX_EXPORT_BATCH_SIZE,
                    _DEFAULT_MAX_EXPORT_BATCH_SIZE,
                )
            )
        except ValueError:
            logger.exception(
                _ENV_VAR_INT_VALUE_ERROR_MESSAGE,
                OTEL_BSP_MAX_EXPORT_BATCH_SIZE,
                _DEFAULT_MAX_EXPORT_BATCH_SIZE,
            )
            return _DEFAULT_MAX_EXPORT_BATCH_SIZE

    @staticmethod
    def _default_export_timeout_millis():
        try:
            return int(
                environ.get(
                    OTEL_BSP_EXPORT_TIMEOUT, _DEFAULT_EXPORT_TIMEOUT_MILLIS
                )
            )
        except ValueError:
            logger.exception(
                _ENV_VAR_INT_VALUE_ERROR_MESSAGE,
                OTEL_BSP_EXPORT_TIMEOUT,
                _DEFAULT_EXPORT_TIMEOUT_MILLIS,
            )
            return _DEFAULT_EXPORT_TIMEOUT_MILLIS

    @staticmethod
    def _validate_arguments(
        max_queue_size, schedule_delay_millis, max_export_batch_size
    ):
        if max_queue_size <= 0:
            raise ValueError("max_queue_size must be a positive integer.")

        if schedule_delay_millis <= 0:
            raise ValueError("schedule_delay_millis must be positive.")

        if max_export_batch_size <= 0:
            raise ValueError(
                "max_export_batch_size must be a positive integer."
            )

        if max_export_batch_size > max_queue_size:
            raise ValueError(
                "max_export_batch_size must be less than or equal to max_queue_size."
            )
