import logging
from queue import Queue
from threading import Thread
from unittest.mock import MagicMock, patch

from eave.collectors.core.agent import _QUEUE_CLOSED_SENTINEL, EaveAgent, QueueParams, TooManyFailuresError
from eave.collectors.core.datastructures import EventPayload

from .base import BaseTestCase


class EaveAgentTest(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.queue_params = QueueParams(flush_frequency_seconds=1, maxsize=10)
        self.agent = EaveAgent(queue_params=self.queue_params, logger=logging.getLogger("eave_test"))

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()
        self.agent.stop()

    def test_is_alive(self):
        self.assertFalse(self.agent.is_alive())

        with patch.object(Thread, "start") as mock_start:
            self.agent.start()
            self.assertTrue(self.agent.is_alive())
            mock_start.assert_called_once()

    def test_start_and_stop(self):
        self.assertFalse(self.agent.is_alive())

        self.agent.start()
        self.assertTrue(self.agent.is_alive())

        with patch.object(self.agent._thread, "join") as mock_join:
            self.agent.stop()
            self.assertFalse(self.agent.is_alive())
            mock_join.assert_called_once_with(timeout=10)

    def test_put(self):
        payload = MagicMock(spec=EventPayload)
        payload.event_type = "test_event"
        payload.to_dict.return_value = {"key": "value"}

        self.agent.put(payload)
        self.assertFalse(self.agent._queue.empty())
        item = self.agent._queue.get()
        self.assertEqual(item, ("test_event", {"key": "value"}))

    def test_put_queue_full(self):
        # If the queue was bounded (it isn't by default), this would test the exception handling.
        with patch("eave.collectors.core.logging.EAVE_LOGGER.exception") as mock_exception:
            self.agent._queue = Queue(maxsize=1)
            self.agent._queue.put(("dummy_event", {"key": "value"}))

            payload = MagicMock(spec=EventPayload)
            payload.event_type = "test_event"
            payload.to_dict.return_value = {"key": "value"}

            self.agent.put(payload)
            mock_exception.assert_called_once()

    def test_worker_event_loop(self):
        with patch("asyncio.run") as mock_asyncio_run:
            self.agent._worker_event_loop()
            mock_asyncio_run.assert_called_once()

    def test_worker_processes_events(self):
        payload = MagicMock(spec=EventPayload)
        payload.event_type = "test_event"
        payload.to_dict.return_value = {"key": "value"}

        # Pre-fill the queue with an event
        self.agent._queue.put((payload.event_type, payload.to_dict()))
        self.agent._queue.put(_QUEUE_CLOSED_SENTINEL)

        with patch("eave.collectors.core.ingest_api.send_batch") as mock_send_batch:
            with patch("eave.collectors.core.logging.EAVE_LOGGER.info") as mock_info_logger:
                with patch("eave.collectors.core.logging.EAVE_LOGGER.debug") as mock_debug_logger:
                    with patch("time.time", side_effect=[0, 0.5, 1, 1.5]):
                        # Run the worker to process the event
                        with patch("asyncio.run") as mock_asyncio_run:
                            mock_asyncio_run.side_effect = lambda coro: coro.send(None)  # to bypass asyncio.run
                            self.agent._worker_event_loop()
                            mock_send_batch.assert_called_once_with(events={"test_event": [{"key": "value"}]})
                            mock_info_logger.assert_any_call("Eave agent complete. Terminating.")

    def test_worker_failsafe(self):
        payload = MagicMock(spec=EventPayload)
        payload.event_type = "test_event"
        payload.to_dict.return_value = {"key": "value"}

        # Pre-fill the queue with a failing event
        self.agent._queue.put((payload.event_type, payload.to_dict()))

        with patch("eave.collectors.core.ingest_api.send_batch", side_effect=Exception("Network Error")):
            with patch("eave.collectors.core.logging.EAVE_LOGGER.exception") as mock_logger:
                with self.assertRaises(TooManyFailuresError):
                    with patch("time.time", side_effect=[0, 0.5, 1, 1.5]):
                        with patch("asyncio.run") as mock_asyncio_run:
                            mock_asyncio_run.side_effect = lambda coro: coro.send(None)
                            self.agent._worker_event_loop()
                            mock_logger.assert_called()

    def test_stop_while_not_running(self):
        self.agent.stop()  # Should simply return without error

    def test_stop_after_start(self):
        self.agent.start()
        self.agent.stop()
        self.assertFalse(self.agent.is_alive())

    def test_worker_empty_queue(self):
        with patch("eave.collectors.core.ingest_api.send_batch") as mock_send_batch:
            with patch("time.time", side_effect=[0, 1, 2, 3]):
                with patch("asyncio.run") as mock_asyncio_run:
                    mock_asyncio_run.side_effect = lambda coro: coro.send(None)
                    self.agent._queue.put(_QUEUE_CLOSED_SENTINEL)
                    self.agent._worker_event_loop()
                    mock_send_batch.assert_not_called()
