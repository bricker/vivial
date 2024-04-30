import unittest

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from eave.collectors.core.datastructures import EventPayload, EventType, NetworkEventPayload
from eave.collectors.core.write_queue import BatchWriteQueue, QueueParams
from eave.collectors.starlette.private.collector import StarletteCollector


class ConsoleOutputBatchWriteQueue(BatchWriteQueue):
    _running: bool = False
    queue: list[EventPayload]

    def __init__(self, event_type: EventType) -> None:
        super().__init__(queue_params=QueueParams(event_type=event_type))
        self.queue = []

    def start_autoflush(self) -> None:
        self._running = True

    def stop_autoflush(self) -> None:
        self._running = False

    def put(self, payload: EventPayload) -> None:
        if not self._running:
            raise RuntimeError("queue processor not running")

        self.queue.append(payload)


class StarletteCollectorTestBase(unittest.IsolatedAsyncioTestCase):
    def _create_starlette_app(self) -> Starlette:
        async def test_endpoint(request):
            return PlainTextResponse("Hello!")

        app = Starlette(
            routes=[
                Route("/test", test_endpoint, methods=["GET"]),
            ]
        )
        return app

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self._collector = StarletteCollector(credentials=None)
        self._write_queue = ConsoleOutputBatchWriteQueue(EventType.network_event)
        self._collector.write_queue = self._write_queue
        self._app = self._create_starlette_app()
        self._collector._instrument_app(self._app)
        self._client = TestClient(self._app)

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()
        self._collector._uninstrument_app(self._app)

    async def test_get_request_collected(self) -> None:
        assert len(self._write_queue.queue) == 0

        # WHEN get request is made to instrumented app
        self._client.get("/test")

        # THEN network event is pushed to write_queue
        assert len(self._write_queue.queue) == 1
        e = self._write_queue.queue[0]
        assert isinstance(e, NetworkEventPayload)
        # TODO: event content assertions
