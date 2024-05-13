import time
from urllib.parse import urlencode

import aiohttp
import jwt
from aiohttp.hdrs import METH_GET
from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send

from eave.core.internal import database
from eave.core.internal.orm.account import AccountOrm
from eave.core.internal.orm.metabase_instance import MetabaseInstanceOrm
from eave.stdlib.api_util import get_header_value
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.cookies import EAVE_EMBED_COOKIE_PREFIX, set_http_cookie
from eave.stdlib.exceptions import NotFoundError
from eave.stdlib.http_endpoint import HTTPEndpoint
from eave.stdlib.logging import LOGGER, LogContext
from eave.stdlib.util import ensure_uuid

_METABASE_UI_QP = {
    "top_nav": "true",
    "new_button": "true",
    "logo": "false",
    "side_nav": "false",
    "breadcrumbs": "false",
    "search": "false",
    "header": "false",
    "action_buttons": "false",
}

_METABASE_SESSION_COOKIE_NAMES = [
    "SESSION",
    "TIMEOUT",
    "DEVICE",
]

_METABASE_COOKIE_PREFIX = "metabase."


class MetabaseProxyRouter:
    """
    Routes incoming requests to host embed.eave.fyi to the metabase proxy endpoints.
    """

    app: ASGIApp

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            request = Request(scope=scope)
            if request.url.hostname == SHARED_CONFIG.eave_embed_hostname_public:
                original_path = scope["path"]
                scope["path"] = f"/_/metabase/proxy{original_path}"

        await self.app(scope, receive, send)


class MetabaseProxyEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        async with database.async_session.begin() as db_session:
            metabase_instance = await MetabaseInstanceOrm.one_or_exception(
                session=db_session,
                team_id=ensure_uuid(ctx.eave_authed_team_id),
            )

        mb_cookies: dict[str, str] = {}

        for cookie_name in _METABASE_SESSION_COOKIE_NAMES:
            cookie_value = request.cookies.get(f"{EAVE_EMBED_COOKIE_PREFIX}{cookie_name}")
            if cookie_value:
                mb_cookies[f"{_METABASE_COOKIE_PREFIX}{cookie_name}"] = cookie_value

        original_path = request.path_params["rest"]
        original_body = await request.body()

        new_headers: dict[str, str] = {}
        new_headers["X-Metabase-Embedded"] = "true"

        for header in [aiohttp.hdrs.ACCEPT, aiohttp.hdrs.ACCEPT_ENCODING, aiohttp.hdrs.CONTENT_TYPE]:
            if h := get_header_value(scope=scope, name=header):
                new_headers[header] = h

        async with aiohttp.ClientSession() as session:
            # Get the response from Metabase
            mb_response = await session.request(
                method=request.method,
                url=f"{metabase_instance.internal_base_url}/{original_path}",
                cookies=mb_cookies,
                data=original_body,
                params={
                    **request.query_params,
                    # **_METABASE_UI_QP,
                },
                headers=new_headers,
                allow_redirects=False,
            )

            # Don't forward error messages downstream
            mb_response.raise_for_status()

            # Consume the body while the session is still open
            body = await mb_response.read()

        LOGGER.info(
            "metabase response",
            ctx,
            {"mb": {"headers": dict(mb_response.headers), "status": mb_response.status}},
        )

        mb_response = Response(
            status_code=mb_response.status,
            content=body,
            media_type=mb_response.content_type,
        )

        return mb_response


class MetabaseAuthEndpoint(HTTPEndpoint):
    async def handle(self, request: Request, scope: HTTPScope, ctx: LogContext) -> Response:
        """
        Redirects request to the authenticated user's metabase instance to set SSO
        cookies before redirecting in turn to the metabase dashboard specified in the
        `return_to` query parameter.
        This endpoint resolves to a redirect to an HTML page on success and is intended
        to be the src for an iframe element.
        """
        async with database.async_session.begin() as db_session:
            account = await AccountOrm.one_or_exception(
                session=db_session,
                params=AccountOrm.QueryParams(
                    id=ensure_uuid(ctx.eave_authed_account_id),
                ),
            )

            metabase_instance = await MetabaseInstanceOrm.one_or_exception(
                session=db_session,
                team_id=account.team_id,
            )

        if not metabase_instance.jwt_signing_key or not metabase_instance.jwt_signing_key:
            raise NotFoundError("Metabase instance can't be reached.")

        email = account.email or "unknown"

        full_jwt = jwt.encode(
            payload={
                "email": email,
                "first_name": email.split("@")[0] or "unknown",
                "exp": round(time.time()) + (60 * 10),  # 10min
            },
            key=metabase_instance.jwt_signing_key,
        )

        # FIXME: Default "1" isn't logical
        dashboard_id = (
            metabase_instance.default_dashboard_id if metabase_instance.default_dashboard_id is not None else "1"
        )

        async with aiohttp.ClientSession() as session:
            # Get the response from Metabase
            # All we really need is the metabase.SESSION cookie from the /auth/sso endpoint.
            # After that, we handle redirects ourselves.
            mb_response = await session.request(
                method=METH_GET,
                url=f"{metabase_instance.internal_base_url}/auth/sso",
                params={
                    "jwt": full_jwt,
                    "return_to": f"/dashboard/{dashboard_id}?{urlencode(_METABASE_UI_QP)}",
                },
                allow_redirects=False,  # This is important, because the /auth/sso endpoint returns Set-Cookie headers that we need to capture.
            )

            mb_response.raise_for_status()

        LOGGER.info(
            "metabase response",
            ctx,
            {"mb": {"headers": dict(mb_response.headers), "status": mb_response.status}},
        )

        response = RedirectResponse(
            status_code=mb_response.status,
            url=mb_response.headers[aiohttp.hdrs.LOCATION],
        )

        for cookie_name in _METABASE_SESSION_COOKIE_NAMES:
            # Replace `metabase.SESSION` etc. with `eave.embed.SESSION`
            # The purpose is to obfuscate the backend embed implementation (metabase)
            if morsel := mb_response.cookies.get(f"{_METABASE_COOKIE_PREFIX}{cookie_name}"):
                set_http_cookie(
                    response=response,
                    key=f"{EAVE_EMBED_COOKIE_PREFIX}{cookie_name}",
                    value=morsel.value,
                    max_age=morsel.get("max_age"),
                    expires=morsel.get("expires"),
                    httponly=True,
                )

        return response
