import contextlib
from collections.abc import AsyncGenerator
from http import HTTPStatus

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

import eave.stdlib.logging
import eave.stdlib.time
from eave.dashboard.config import DASHBOARD_APP_CONFIG
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.headers import MIME_TYPE_BINARY, MIME_TYPE_JSON
from eave.stdlib.status import status_payload

eave.stdlib.time.set_utc()


def status_endpoint(request: Request) -> Response:
    content = status_payload().json()
    response = Response(content=content, status_code=HTTPStatus.OK, media_type=MIME_TYPE_JSON)
    return response


def health_endpoint(request: Request) -> Response:
    return Response(content="1", status_code=HTTPStatus.OK)


def apple_domain_verification_file(request: Request) -> Response:
    return Response(
        content=DASHBOARD_APP_CONFIG.apple_domain_verification_code,
        status_code=HTTPStatus.OK,
        media_type=MIME_TYPE_BINARY,
    )


async def logout_endpoint(request: Request) -> Response:
    response = RedirectResponse(
        url=SHARED_CONFIG.eave_api_base_url_public + "/public/logout",
        status_code=HTTPStatus.PERMANENT_REDIRECT,
    )
    return response


templates = Jinja2Templates(directory="eave/dashboard/templates")


def web_app_endpoint(request: Request) -> Response:
    response = templates.TemplateResponse(
        request,
        "index.html.jinja",
        context={
            "asset_base": SHARED_CONFIG.asset_base,
            "api_base": SHARED_CONFIG.eave_api_base_url_public,
            "analytics_enabled": _python_bool_to_js(SHARED_CONFIG.analytics_enabled),
            "monitoring_enabled": _python_bool_to_js(SHARED_CONFIG.monitoring_enabled),
            "datadog_application_id": DASHBOARD_APP_CONFIG.datadog_application_id,
            "datadog_client_token": DASHBOARD_APP_CONFIG.datadog_client_token,
            "app_env": SHARED_CONFIG.eave_env,
            "app_version": SHARED_CONFIG.app_version,
            "segment_write_key": DASHBOARD_APP_CONFIG.segment_write_key,
            "stripe_publishable_key": SHARED_CONFIG.stripe_publishable_key,
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
        DASHBOARD_APP_CONFIG.preload()

    yield


app = Starlette(
    routes=[
        Mount("/static", StaticFiles(directory="eave/dashboard/static")),
        Route(
            path="/status",
            methods=["GET"],
            endpoint=status_endpoint,
        ),
        Route(path="/healthz", methods=["GET"], endpoint=health_endpoint),
        Route(
            path="/.well-known/apple-developer-merchantid-domain-association",
            methods=["GET"],
            endpoint=apple_domain_verification_file,
        ),
        Route(path="/logout", methods=["GET"], endpoint=logout_endpoint),
        Route(path="/{rest:path}", methods=["GET"], endpoint=web_app_endpoint),
    ],
    lifespan=_app_lifespan,
)


def _python_bool_to_js(v: bool) -> str:  # noqa
    return "true" if v else "false"
