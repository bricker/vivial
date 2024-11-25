from http import HTTPStatus
from uuid import UUID

from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.exceptions import HTTPException
from sqlalchemy.exc import NoResultFound
from eave.core import database
from eave.core.auth_cookies import delete_auth_cookies, set_new_auth_cookies
from eave.core.config import JWT_AUDIENCE, JWT_ISSUER
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.cookies import EAVE_ACCESS_TOKEN_COOKIE_NAME, EAVE_REFRESH_TOKEN_COOKIE_NAME, set_http_cookie
from eave.stdlib.http_exceptions import UnauthorizedError
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.jwt import JWTPurpose, InvalidTokenError, validate_jws_or_exception, validate_jws_pair_or_exception
from eave.stdlib.logging import LogContext
from eave.stdlib.headers import MIME_TYPE_TEXT

from eave.core.orm.account import AccountOrm

class LogoutEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        response = RedirectResponse(
            status_code=HTTPStatus.TEMPORARY_REDIRECT,
            url=SHARED_CONFIG.eave_dashboard_base_url_public,
        )
        delete_auth_cookies(response=response)
        return response
