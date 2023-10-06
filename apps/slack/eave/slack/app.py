from asgiref.typing import ASGI3Application
from eave.stdlib.eave_origins import EaveApp
from eave.stdlib.middleware.origin import OriginASGIMiddleware
from eave.stdlib.middleware.signature_verification import SignatureVerificationASGIMiddleware
import eave.stdlib.requests
from eave.stdlib.slack_api import SlackAppEndpointConfiguration
from eave.stdlib.slack_api.operations import SlackEventProcessorTaskOperation, SlackWebhookOperation
import eave.stdlib.time
from starlette.applications import Starlette
from starlette.routing import Route
from eave.stdlib import cache

from .requests.warmup import StatusRequest, StopRequest, WarmupRequest, StartRequest
from .requests.event_callback import SlackEventCallbackHandler
from .requests.event_processor import SlackEventProcessorTask
from eave.stdlib.middleware import common_middlewares

eave.stdlib.time.set_utc()


def make_route(
    config: SlackAppEndpointConfiguration,
    endpoint: ASGI3Application,
) -> Route:
    if config.signature_required:
        endpoint = SignatureVerificationASGIMiddleware(app=endpoint, endpoint_config=config, audience=EaveApp.eave_api)

    if config.origin_required:
        # First thing to happen when the middleware chain is kicked off
        endpoint = OriginASGIMiddleware(app=endpoint, endpoint_config=config)

    return Route(path=config.path, endpoint=endpoint)


routes = [
    Route("/_ah/warmup", WarmupRequest, methods=["GET"]),
    Route("/_ah/start", StartRequest, methods=["GET"]),
    Route("/_ah/stop", StopRequest, methods=["GET"]),
    Route("/slack/status", StatusRequest, methods=["GET", "POST", "DELETE", "HEAD", "OPTIONS"]),
    make_route(config=SlackWebhookOperation.config, endpoint=SlackEventCallbackHandler),
    make_route(config=SlackEventProcessorTaskOperation.config, endpoint=SlackEventProcessorTask),
]


async def graceful_shutdown() -> None:
    if client := cache.initialized_client():
        await client.close()


api = Starlette(
    middleware=common_middlewares,
    routes=routes,
    on_shutdown=[graceful_shutdown],
)
