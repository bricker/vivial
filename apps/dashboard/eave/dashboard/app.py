from http import HTTPStatus

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

import eave.stdlib.logging
import eave.stdlib.requests_util
import eave.stdlib.time
from eave.collectors.starlette import StarletteCollectorManager
from eave.stdlib.auth_cookies import delete_auth_cookies
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.core_api.operations.status import status_payload
from eave.stdlib.headers import MIME_TYPE_JSON

from .config import DASHBOARD_APP_CONFIG

eave.stdlib.time.set_utc()


def status_endpoint(request: Request) -> Response:
    model = status_payload()
    response = Response(content=model.json(), status_code=HTTPStatus.OK, media_type=MIME_TYPE_JSON)
    return response


def health_endpoint(request: Request) -> Response:
    return Response(content="1", status_code=HTTPStatus.OK)


async def logout_endpoint(request: Request) -> Response:
    response = RedirectResponse(
        url=SHARED_CONFIG.eave_dashboard_base_url_public + "/login", status_code=HTTPStatus.FOUND
    )
    delete_auth_cookies(request=request, response=response)
    return response


templates = Jinja2Templates(directory="eave/dashboard/templates")


def web_app_endpoint(request: Request) -> Response:
    response = templates.TemplateResponse(
        request,
        "index.html.jinja",
        context={
            "asset_base": SHARED_CONFIG.asset_base,
            "collector_asset_base": DASHBOARD_APP_CONFIG.collector_asset_base,
            "eave_client_id": DASHBOARD_APP_CONFIG.eave_client_id,
            "api_base": SHARED_CONFIG.eave_api_base_url_public,
            "embed_base": SHARED_CONFIG.eave_embed_base_url_public,
            "analytics_enabled": SHARED_CONFIG.analytics_enabled,
            "app_env": SHARED_CONFIG.eave_env,
            "app_version": SHARED_CONFIG.app_version,
        },
    )

    return response


app = Starlette(
    routes=[
        Mount("/static", StaticFiles(directory="eave/dashboard/static")),
        Route(
            path="/status",
            methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
            endpoint=status_endpoint,
        ),
        Route(path="/healthz", methods=["GET"], endpoint=health_endpoint),
        Route(path="/logout", methods=["GET"], endpoint=logout_endpoint),
        Route(path="/{rest:path}", methods=["GET"], endpoint=web_app_endpoint),
    ],
)

StarletteCollectorManager.start(app)
