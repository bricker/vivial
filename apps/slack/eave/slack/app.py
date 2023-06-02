import eave.stdlib.api_util as eave_api_util
import eave.stdlib.requests
import eave.stdlib.time
from starlette.applications import Starlette
from starlette.routing import Route, Mount

from .config import SLACK_EVENT_QUEUE_TARGET_PATH

from .requests.warmup import WarmupRequest
from .requests.event_callback import SlackEventCallbackHandler
from .requests.event_processor import SlackEventProcessorTask

eave.stdlib.time.set_utc()


routes = [
    Route("/_ah/warmup", WarmupRequest, methods=["GET"]),
    Route(SLACK_EVENT_QUEUE_TARGET_PATH, SlackEventProcessorTask, methods=["POST"]),
    Mount(
        "/slack",
        routes=[
            *eave_api_util.standard_endpoints_starlette,
            Route("/events", SlackEventCallbackHandler, methods=["POST"]),
        ],
    ),
]

api = Starlette(routes=routes)
