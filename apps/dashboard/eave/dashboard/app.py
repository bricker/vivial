from collections.abc import Awaitable, Callable
from functools import wraps
from http import HTTPStatus

from aiohttp import ClientResponseError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

import eave.stdlib.logging
import eave.stdlib.requests_util
import eave.stdlib.time
from eave.stdlib.auth_cookies import AuthCookies, delete_auth_cookies, get_auth_cookies, set_auth_cookies
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.cookies import delete_http_cookie, set_http_cookie
from eave.stdlib.core_api.models.virtual_event import VirtualEventQueryInput
from eave.stdlib.core_api.operations import account, team, virtual_event
from eave.stdlib.core_api.operations.metabase_embedding_sso import MetabaseEmbeddingSSOOperation
from eave.stdlib.core_api.operations.status import status_payload
from eave.stdlib.endpoints import BaseResponseBody
from eave.stdlib.exceptions import UnauthorizedError
from eave.stdlib.util import ensure_uuid, unwrap
from eave.stdlib.utm_cookies import set_tracking_cookies

from .config import DASHBOARD_APP_CONFIG

eave.stdlib.time.set_utc()


def _auth_handler(f: Callable[[Request, AuthCookies], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]:
    @wraps(f)
    async def wrapper(request: Request) -> Response:
        try:
            auth_cookies = _get_auth_cookies_or_exception(request=request)
            r = await f(request, auth_cookies)
            return r
        except (ClientResponseError, UnauthorizedError) as e:
            if e.code == HTTPStatus.UNAUTHORIZED:
                response = Response(status_code=HTTPStatus.UNAUTHORIZED)
                delete_auth_cookies(response)
                return response
            else:
                raise

    return wrapper


def status_endpoint() -> str:
    model = status_payload()
    return model.json()


@_auth_handler
async def get_user_endpoint(request: Request, auth_cookies: AuthCookies) -> Response:
    eave_response = await account.GetAuthenticatedAccount.perform(
        origin=DASHBOARD_APP_CONFIG.eave_origin,
        team_id=ensure_uuid(auth_cookies.team_id),
        account_id=ensure_uuid(auth_cookies.account_id),
        access_token=unwrap(auth_cookies.access_token),
    )

    return _make_response(eave_response)


@_auth_handler
async def get_virtual_events_endpoint(request: Request, auth_cookies: AuthCookies) -> Response:
    body = await request.json()
    query_input: VirtualEventQueryInput | None = body.get("query")

    eave_response = await virtual_event.GetVirtualEventsRequest.perform(
        origin=DASHBOARD_APP_CONFIG.eave_origin,
        team_id=ensure_uuid(auth_cookies.team_id),
        account_id=ensure_uuid(auth_cookies.account_id),
        access_token=unwrap(auth_cookies.access_token),
        input=virtual_event.GetVirtualEventsRequest.RequestBody(virtual_events=query_input),
    )

    return _make_response(eave_response)


@_auth_handler
async def get_team_endpoint(request: Request, auth_cookies: AuthCookies) -> Response:
    eave_response = await team.GetTeamRequest.perform(
        origin=DASHBOARD_APP_CONFIG.eave_origin,
        team_id=unwrap(auth_cookies.team_id),
        account_id=ensure_uuid(auth_cookies.account_id),
        access_token=unwrap(auth_cookies.access_token),
    )

    return _make_response(eave_response)


@_auth_handler
async def embed_metabase_endpoint(request: Request, auth_cookies: AuthCookies) -> Response:
    resp = await MetabaseEmbeddingSSOOperation.perform(
        input=MetabaseEmbeddingSSOOperation.RequestBody(return_to=request.query_params.get("return_to")),
        origin=DASHBOARD_APP_CONFIG.eave_origin,
        team_id=unwrap(auth_cookies.team_id),
        account_id=ensure_uuid(auth_cookies.account_id),
        access_token=unwrap(auth_cookies.access_token),
    )

    return await _make_redirect_response(eave_response=resp)


async def logout_endpoint(request: Request) -> Response:
    response = RedirectResponse(url=SHARED_CONFIG.eave_public_dashboard_base + "/login", status_code=HTTPStatus.FOUND)
    delete_auth_cookies(response=response)
    _delete_login_state_hint_cookie(response=response)
    return response


templates = Jinja2Templates(directory="eave/dashboard/templates")


def web_app_endpoint(request: Request) -> Response:
    response = templates.TemplateResponse(
        request,
        "index.html.jinja",
        context={
            "asset_base": SHARED_CONFIG.asset_base,
            "cookie_domain": SHARED_CONFIG.eave_cookie_domain,
            "api_base": SHARED_CONFIG.eave_public_api_base,
            "analytics_enabled": SHARED_CONFIG.analytics_enabled,
            "app_env": SHARED_CONFIG.eave_env,
            "app_version": SHARED_CONFIG.app_version,
        },
    )

    set_tracking_cookies(response=response, request=request)

    auth_cookies = get_auth_cookies(request.cookies)
    if auth_cookies.all_set:
        _set_login_state_hint_cookie(response=response)
    else:
        _delete_login_state_hint_cookie(response=response)

    return response


_EAVE_LOGIN_STATE_HINT_COOKIE_NAME = "ev_login_state_hint.202311"


def _set_login_state_hint_cookie(response: Response) -> None:
    # This cookie is a HINT to the client whether the user may be logged in.
    # It doesn't actually indicate the logged-in state, but the client can use this cookie to decide if it can skip some API calls, for example.
    # This cookie is set to httponly=False so the client can read it.
    set_http_cookie(response=response, key=_EAVE_LOGIN_STATE_HINT_COOKIE_NAME, value="1", httponly=False)


def _delete_login_state_hint_cookie(response: Response) -> None:
    delete_http_cookie(response=response, key=_EAVE_LOGIN_STATE_HINT_COOKIE_NAME, httponly=False)


def _get_auth_cookies_or_exception(request: Request) -> AuthCookies:
    auth_cookies = get_auth_cookies(request.cookies)
    if not auth_cookies.all_set:
        raise UnauthorizedError()

    return auth_cookies


async def _make_redirect_response(eave_response: BaseResponseBody) -> Response:
    assert eave_response.raw_response, "invalid eave response"
    headers = dict(eave_response.raw_response.headers)
    status = eave_response.raw_response.status
    response = Response(
        headers=headers,
        status_code=status,
    )

    return response


def _make_response(eave_response: BaseResponseBody) -> Response:
    response = JSONResponse(content=eave_response.json())

    if eave_response.cookies:
        cookies = get_auth_cookies(cookies=eave_response.cookies)
        set_auth_cookies(
            response=response, access_token=cookies.access_token, account_id=cookies.account_id, team_id=cookies.team_id
        )

    return response


app = Starlette(
    routes=[
        Mount("/static", StaticFiles(directory="eave/dashboard/static")),
        Route(path="/status", methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"], endpoint=status_endpoint),
        Route(path="/api/me", methods=["POST"], endpoint=get_user_endpoint),
        Route(path="/api/team/virtual-events", methods=["POST"], endpoint=get_virtual_events_endpoint),
        Route(path="/api/team", methods=["POST"], endpoint=get_team_endpoint),
        Route(path="/embed/metabase", methods=["GET"], endpoint=embed_metabase_endpoint),
        Route(path="/logout", methods=["GET"], endpoint=logout_endpoint),
        Route(path="/{rest:path}", methods=["GET"], endpoint=web_app_endpoint),
    ],
)
