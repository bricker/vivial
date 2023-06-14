import eave.stdlib.api_util as eave_api_util
import eave.stdlib.requests
import eave.stdlib.time
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from eave.stdlib import cache

from .config import SLACK_EVENT_QUEUE_TARGET_PATH

from .requests.warmup import WarmupRequest
from .requests.event_callback import SlackEventCallbackHandler
from .requests.event_processor import SlackEventProcessorTask
from eave.stdlib.middleware import standard_middleware_starlette

eave.stdlib.time.set_utc()


routes = [
    Route("/_ah/warmup", WarmupRequest, methods=["GET"]),
    Route(SLACK_EVENT_QUEUE_TARGET_PATH, SlackEventProcessorTask, methods=["POST"]),
    Mount(
        "/slack",
        routes=[
            eave_api_util.StatusRoute,
            Route("/events", SlackEventCallbackHandler, methods=["POST"]),
        ],
        # TODO: Add mounts for API with signature & origin verification
    ),
]


async def graceful_shutdown() -> None:
    if cache.initialized():
        await cache.client().close()


api = Starlette(
    middleware=standard_middleware_starlette,
    routes=routes,
    on_shutdown=[graceful_shutdown],
)
