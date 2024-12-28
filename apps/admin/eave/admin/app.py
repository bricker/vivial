import contextlib
from collections.abc import AsyncGenerator
from http import HTTPStatus

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

import eave.stdlib.logging
from eave.stdlib.middleware.iap_jwt_validation import IAPJWTValidationMiddleware
import eave.stdlib.time
from eave.admin.config import ADMIN_APP_CONFIG
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.headers import MIME_TYPE_JSON
from eave.stdlib.status import status_payload

eave.stdlib.time.set_utc()


def status_endpoint(request: Request) -> Response:
    content = status_payload().json()
    response = Response(content=content, status_code=HTTPStatus.OK, media_type=MIME_TYPE_JSON)
    return response


def health_endpoint(request: Request) -> Response:
    return Response(content="1", status_code=HTTPStatus.OK)


templates = Jinja2Templates(directory="eave/admin/templates")


def web_app_endpoint(request: Request) -> Response:
    response = templates.TemplateResponse(
        request,
        "index.html.jinja",
        context={
            "asset_base": SHARED_CONFIG.asset_base,
            "api_base": SHARED_CONFIG.eave_api_base_url_public,
            "app_env": SHARED_CONFIG.eave_env,
            "app_version": SHARED_CONFIG.app_version,
        },
    )

    return response


@contextlib.asynccontextmanager
async def _app_lifespan(app: Starlette) -> AsyncGenerator[None, None]:
    if not SHARED_CONFIG.is_local:
        # Preload config in production environments.
        # The idea here is that in development, secrets and required envs
        # should be lazily evaluated, but in production environments
        # we want to attempt to load them before the application starts up,
        # so that it will fail to start if anything required is unavailable.
        SHARED_CONFIG.preload()
        ADMIN_APP_CONFIG.preload()

    yield


app = Starlette(
    routes=[
        Mount("/static", StaticFiles(directory="eave/admin/static")),
        Route(
            path="/status",
            methods=["GET"],
            endpoint=status_endpoint,
        ),
        Route(path="/healthz", methods=["GET"], endpoint=health_endpoint),
        Route(path="/{rest:path}", methods=["GET"], endpoint=web_app_endpoint),
    ],
    lifespan=_app_lifespan,
    middleware=[
        Middleware(IAPJWTValidationMiddleware, aud=ADMIN_APP_CONFIG.iap_jwt_aud)
    ],
)
