from eave.stdlib.endpoints import StatusRoute
import eave.stdlib.requests
import eave.stdlib.time
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from eave.stdlib import cache

from .config import SLACK_EVENT_QUEUE_TARGET_PATH

from .requests.warmup import StopRequest, WarmupRequest, StartRequest
from .requests.event_callback import SlackEventCallbackHandler
from .requests.event_processor import SlackEventProcessorTask
from eave.stdlib.middleware import common_middlewares, common_internal_api_middlewares

eave.stdlib.time.set_utc()


routes = [
    Route("/_ah/warmup", WarmupRequest, methods=["GET"]),
    Route("/_ah/start", StartRequest, methods=["GET"]),
    Route("/_ah/stop", StopRequest, methods=["GET"]),

    Mount(
        "/slack",
        routes=[
            StatusRoute,
            Route("/events", SlackEventCallbackHandler, methods=["POST"]),
        ],
    ),

    Mount(
        "/_/slack/tasks",
        middleware=common_internal_api_middlewares,
        routes=[
            Route("/events", SlackEventProcessorTask, methods=["POST"]),
        ],
    ),
]


async def graceful_shutdown() -> None:
    if cache.initialized():
        await cache.client().close()


api = Starlette(
    middleware=common_middlewares,
    routes=routes,
    on_shutdown=[graceful_shutdown],
)
