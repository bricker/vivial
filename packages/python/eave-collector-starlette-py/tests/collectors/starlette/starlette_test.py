import json
import unittest
import urllib.parse

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse, Response
from starlette.routing import Route
from starlette.testclient import TestClient

from eave.collectors.core.correlation_context import CORR_CTX
from eave.collectors.core.correlation_context.base import EAVE_COLLECTOR_COOKIE_PREFIX
from eave.collectors.core.datastructures import HttpServerEventPayload
from eave.collectors.core.test_util import EphemeralWriteQueue
from eave.collectors.starlette.private.collector import StarletteCollector


class StarletteCollectorTestBase(unittest.IsolatedAsyncioTestCase):
    def _create_starlette_app(self) -> Starlette:
        async def test_endpoint(request: Request) -> Response:
            return PlainTextResponse("Hello!")

        async def test_json_endpoint(request: Request) -> Response:
            body = await request.json()
            return JSONResponse(body)

        async def ctx_set_endpoint(request: Request) -> Response:
            body = request.query_params
            for k, v in body.items():
                CORR_CTX.set(k, v, encrypt=False)
            return PlainTextResponse("cookies changed")

        app = Starlette(
            routes=[
                Route("/test", test_endpoint, methods=["GET"]),
                Route("/json", test_json_endpoint, methods=["POST"]),
                Route("/set_ctx", ctx_set_endpoint, methods=["GET"]),
            ]
        )
        return app

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self._collector = StarletteCollector()
        self._write_queue = EphemeralWriteQueue()
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

        # THEN network event is pushed to write_queue
        assert len(self._write_queue.queue) == 1
        e1 = self._write_queue.queue[0]
        assert isinstance(e1, HttpServerEventPayload), "First event was not a server network event"
        assert e1.request_payload == "", "GET request has unexpected payload"

    async def test_body_read(self) -> None:
        assert len(self._write_queue.queue) == 0

        body = {"foo": "bar"}

        # WHEN post request is made to instrumented app
        response = self._client.post("/json", json=body)

        # THEN network event is pushed to write_queue
        assert response.status_code == 200
        assert len(self._write_queue.queue) == 1
        e1 = self._write_queue.queue[0]
        assert isinstance(e1, HttpServerEventPayload), "First event was not a server network event"
        assert e1.request_payload == json.dumps(body), "POST request has unexpected payload"

    async def test_eave_ctx_set_from_cookies(self) -> None:
        # GIVEN eave cookies set on request
        valid_cookie = f"{EAVE_COLLECTOR_COOKIE_PREFIX}test_cookie"
        json_cookie = f"{EAVE_COLLECTOR_COOKIE_PREFIX}json"
        non_eave_cookie = "no_eave_prefix"
        ctx_key = "some_ctx_key"
        self._client.cookies.set(valid_cookie, "valid")
        self._client.cookies.set(json_cookie, f'{{"{ctx_key}": 123}}')
        self._client.cookies.set(non_eave_cookie, "invalid")

        # WHEN request made
        self._client.get("/test")

        # THEN cookie values set in eave ctx
        assert len(self._write_queue.queue) > 0
        e = self._write_queue.queue[0]
        assert isinstance(e, HttpServerEventPayload)
        assert e.corr_ctx is not None, "Eave context was expected to be set in the network event"
        assert e.corr_ctx.get(valid_cookie) == "valid"
        assert e.corr_ctx.get(non_eave_cookie) is None
        assert e.corr_ctx.get(json_cookie) == f'{{"{ctx_key}": 123}}'

    async def test_response_cookie_ctx_set(self) -> None:
        # GIVEN there is some ctx cookies that can be changed
        self._client.cookies.set(f"{EAVE_COLLECTOR_COOKIE_PREFIX}unchanged_cookie", "valid")
        self._client.cookies.set(f"{EAVE_COLLECTOR_COOKIE_PREFIX}changed_cookie", "change_me")

        # WHEN corr ctx is changed/created server-side
        # NOTE: couldnt use post+json body bcus TestClient cannot handle async responses,
        #       and reading request.json() is async
        resp = self._client.get("/set_ctx?changed_cookie=new_value&new_cookie=shiny")

        # THEN only changed values are set in cookies
        assert resp is not None
        assert resp.cookies.get(f"{EAVE_COLLECTOR_COOKIE_PREFIX}unchanged_cookie") is None
        assert resp.cookies.get(f"{EAVE_COLLECTOR_COOKIE_PREFIX}changed_cookie") == urllib.parse.quote_plus("new_value")
        assert resp.cookies.get(f"{EAVE_COLLECTOR_COOKIE_PREFIX}new_cookie") == "shiny"
