import unittest

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from eave.collectors.core.datastructures import EventType, NetworkEventPayload
from eave.collectors.starlette.private.collector import StarletteCollector

from ...mock_write_queue import ConsoleOutputBatchWriteQueue


class StarletteCollectorTestBase(unittest.IsolatedAsyncioTestCase):
    def _create_starlette_app() -> Starlette:
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
