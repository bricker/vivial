from http import HTTPStatus

from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from eave.core.auth_cookies import delete_auth_cookies
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LogContext


class LogoutEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        response = RedirectResponse(
            status_code=HTTPStatus.TEMPORARY_REDIRECT,
            url=SHARED_CONFIG.eave_dashboard_base_url_public,
        )
        delete_auth_cookies(response=response)
        return response
