import logging
from queue import Queue
from unittest.mock import MagicMock, patch

from eave.collectors.core.agent import (
    _QUEUE_CLOSED_SENTINEL,
    EaveAgent,
    QueueParams,
    TooManyFailuresError,
)
from eave.collectors.core.agent.data_handler.atoms import AtomHandler
from eave.collectors.core.datastructures import EventPayload

from .base import BaseTestCase


class EaveAgentTest(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.queue_params = QueueParams(flush_frequency_seconds=1, maxsize=10)
        self.agent = EaveAgent(
            queue_params=self.queue_params,
            logger=logging.getLogger("eave_test"),
            data_handler=AtomHandler(),
        )

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()
        self.agent.stop()

    def test_is_alive(self):
        self.assertFalse(self.agent.is_alive())

        self.agent.start()
        self.assertTrue(self.agent.is_alive())

    def test_start_and_stop(self):
        self.assertFalse(self.agent.is_alive())

        self.agent.start()
        self.assertTrue(self.agent.is_alive())

        with patch.object(self.agent._thread, "join") as mock_join:  # noqa: SLF001
            self.agent.stop()
            self.assertFalse(self.agent.is_alive())
            mock_join.assert_called_once_with(timeout=10)

    def test_put(self):
        payload = EventPayload(
            event_id="id",
            timestamp=0.0,
            corr_ctx={"key": "value"},
        )

        self.agent.put(payload)
        self.assertFalse(self.agent.queue.empty())
        item = self.agent.queue.get()
        self.assertEqual(item, payload)

    def test_put_queue_full(self):
        self.skipTest("Not implemented")
        # If the queue was bounded (it isn't by default), this would test the exception handling.
        with patch("eave.collectors.core.logging._EAVE_ROOT_LOGGER.exception") as mock_exception:
            self.agent.queue = Queue(maxsize=1)
            self.agent.queue.put(("dummy_event", {"key": "value"}))

            payload = MagicMock(spec=EventPayload)
            payload.event_type = "test_event"
            payload.to_dict.return_value = {"key": "value"}

            self.agent.put(payload)
            mock_exception.assert_called_once()

    def test_worker_processes_events(self):
        payload = EventPayload(event_id="id", timestamp=0, corr_ctx={})

        # Pre-fill the queue with an event
        self.agent.queue.put(payload)
        self.agent.queue.put(_QUEUE_CLOSED_SENTINEL)

        with patch("eave.collectors.core.agent.data_handler.atoms.AtomHandler.send_buffer") as mock_send_batch:
            with patch("logging.Logger.info"):
                self.agent._worker_event_loop()  # noqa: SLF001
                mock_send_batch.assert_called_once()

    def test_worker_failsafe(self):
        # Pre-fill the queue with an event
        self.agent.queue.put(EventPayload(event_id="id", timestamp=0, corr_ctx={}))

        # patch send function to mock network error
        with patch(
            "eave.collectors.core.agent.data_handler.atoms.AtomHandler.send_buffer",
            side_effect=Exception("Network Error"),
        ):
            with patch("logging.Logger.exception") as mock_logger:
                self.agent._worker_event_loop()  # noqa: SLF001
                mock_logger.assert_called()
                logged_exception = mock_logger.call_args[0][0]
                self.assertIsInstance(logged_exception, TooManyFailuresError)
                self.assertEqual(str(logged_exception), "Eave agent failsafe threshold reached! Terminating.")
                assert not self.agent.is_alive()

    def test_stop_while_not_running(self):
        self.agent.stop()  # Should simply return without error
        assert not self.agent.is_alive()
