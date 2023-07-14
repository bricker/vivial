from eave.stdlib.endpoints import StatusRoute
import eave.stdlib.requests
import eave.stdlib.time
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from .requests.warmup import StopRequest, WarmupRequest, StartRequest
from eave.stdlib.middleware import standard_middleware_starlette

eave.stdlib.time.set_utc()


routes = [
    Route("/_ah/warmup", WarmupRequest, methods=["GET"]),
    Route("/_ah/start", StartRequest, methods=["GET"]),
    Route("/_ah/stop", StopRequest, methods=["GET"]),
    Mount(
        "/{{service_name}}",
        routes=[
            StatusRoute,
        ],
    ),
]


async def graceful_shutdown() -> None:
    # Do any shutdown operations here.
    # For example, if you're using cache, close the cache connection here.
    pass

app = Starlette(
    middleware=standard_middleware_starlette,
    routes=routes,
    on_shutdown=[graceful_shutdown],
)
