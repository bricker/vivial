import unittest

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from eave.collectors.core.correlation_context.base import CONTEXT_NAME, COOKIE_PREFIX
from eave.collectors.core.datastructures import EventPayload, EventType, ServerRequestEventPayload
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
        self._collector = StarletteCollector()
        self._write_queue = ConsoleOutputBatchWriteQueue(EventType.server_event)
        self._collector.write_queue = self._write_queue
        self._app = self._create_starlette_app()
        self._collector.instrument_app(self._app)
        self._client = TestClient(self._app)

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()
        self._collector.uninstrument_app(self._app)

    async def test_get_request_collected(self) -> None:
        assert len(self._write_queue.queue) == 0

        # WHEN get request is made to instrumented app
        self._client.get("/test")

        # THEN network events (request + response) are pushed to write_queue
        assert len(self._write_queue.queue) == 2
        e1 = self._write_queue.queue[0]
        e2 = self._write_queue.queue[1]
        assert isinstance(e1, ServerRequestEventPayload), "First event was not a server network event"
        assert isinstance(e2, ServerRequestEventPayload), "Second event was not a server network event"
        assert e1.request_payload == "", "GET request has unexpected payload"
        assert e2.request_payload == "Hello!", "Response body was not recorded"

    async def test_eave_ctx_set_from_cookies(self) -> None:
        # GIVEN eave cookies set on request
        valid_cookie = f"{COOKIE_PREFIX}test_cookie"
        non_eave_cookie = "no_eave_prefix"
        ctx_key = "some_ctx_key"
        self._client.cookies.set(valid_cookie, "valid")
        self._client.cookies.set(CONTEXT_NAME, f'{{"{ctx_key}": 123}}')
        self._client.cookies.set(non_eave_cookie, "invalid")

        # WHEN request made
        self._client.get("/test")

        # THEN cookie values set in eave ctx
        assert len(self._write_queue.queue) > 0
        e = self._write_queue.queue[0]
        assert isinstance(e, ServerRequestEventPayload)
        assert e.context is not None, "Eave context was expected to be set in the network event"
        assert e.context.get(valid_cookie) == "valid"
        assert e.context.get(non_eave_cookie) is None
        assert e.context.get(CONTEXT_NAME) == {ctx_key: 123}
