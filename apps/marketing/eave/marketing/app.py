import json
from functools import wraps
from http.client import UNAUTHORIZED
from typing import Any, Awaitable, Callable, Optional

import werkzeug.exceptions
from aiohttp import ClientResponseError
from flask import Flask, Response, make_response, redirect, render_template, request
from werkzeug.wrappers import Response as BaseResponse

import eave.stdlib.core_api.operations.account as account
import eave.stdlib.core_api.operations.team as team
import eave.stdlib.core_api.operations.virtual_event as virtual_event
import eave.stdlib.logging
import eave.stdlib.requests_util
import eave.stdlib.time
from eave.stdlib.auth_cookies import AuthCookies, delete_auth_cookies, get_auth_cookies, set_auth_cookies
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.cookies import delete_http_cookie, set_http_cookie
from eave.stdlib.core_api.models.virtual_event import VirtualEventQueryInput
from eave.stdlib.core_api.operations.metabase_embedding_sso import MetabaseEmbeddingSSOOperation
from eave.stdlib.endpoints import BaseResponseBody, status_payload
from eave.stdlib.headers import MIME_TYPE_JSON
from eave.stdlib.typing import JsonObject
from eave.stdlib.util import ensure_uuid, unwrap
from eave.stdlib.utm_cookies import set_tracking_cookies

from .config import MARKETING_APP_CONFIG

eave.stdlib.time.set_utc()

app = Flask(__name__)


def _auth_handler(f: Callable[..., Awaitable[Response]]) -> Callable[..., Awaitable[Response]]:
    @wraps(f)
    async def wrapper(*args: Any, **kwargs: Any) -> Response:
        try:
            r = await f(*args, **kwargs)
            return r
        except ClientResponseError as e:
            if e.code == UNAUTHORIZED:
                response = Response(status=UNAUTHORIZED)
                delete_auth_cookies(response)
                return response
            else:
                raise

    return wrapper


@app.get("/status")
def status() -> str:
    model = status_payload()
    return model.json()


@app.route("/_ah/warmup", methods=["GET"])
async def warmup() -> str:
    SHARED_CONFIG.preload()
    MARKETING_APP_CONFIG.preload()
    return "OK"


@app.route("/_ah/start", methods=["GET"])
async def start() -> str:
    return "OK"


@app.route("/_ah/stop", methods=["GET"])
async def stop() -> str:
    return "OK"


def _render_spa(**kwargs: Any) -> str:
    return render_template(
        "index.html.jinja",
        asset_base=SHARED_CONFIG.asset_base,
        cookie_domain=SHARED_CONFIG.eave_cookie_domain,
        api_base=SHARED_CONFIG.eave_public_api_base,
        analytics_enabled=SHARED_CONFIG.analytics_enabled,
        app_env=SHARED_CONFIG.eave_env,
        app_version=SHARED_CONFIG.app_version,
        **kwargs,
    )


@app.route("/dashboard/me", methods=["POST"])
@_auth_handler
async def get_user() -> Response:
    auth_cookies = _get_auth_cookies_or_exception()

    eave_response = await account.GetAuthenticatedAccount.perform(
        origin=MARKETING_APP_CONFIG.eave_origin,
        team_id=ensure_uuid(auth_cookies.team_id),
        account_id=ensure_uuid(auth_cookies.account_id),
        access_token=unwrap(auth_cookies.access_token),
    )

    return _make_response(eave_response)


@app.route("/dashboard/team/virtual-events", methods=["POST"])
@_auth_handler
async def get_virtual_events() -> Response:
    auth_cookies = _get_auth_cookies_or_exception()

    body = request.get_json()
    query_input: Optional[VirtualEventQueryInput] = body.get("query")

    eave_response = await virtual_event.GetVirtualEventsRequest.perform(
        origin=MARKETING_APP_CONFIG.eave_origin,
        team_id=ensure_uuid(auth_cookies.team_id),
        account_id=ensure_uuid(auth_cookies.account_id),
        access_token=unwrap(auth_cookies.access_token),
        input=virtual_event.GetVirtualEventsRequest.RequestBody(virtual_events=query_input),
    )

    return _make_response(eave_response)


@app.route("/dashboard/team", methods=["POST"])
@_auth_handler
async def get_team() -> Response:
    auth_cookies = _get_auth_cookies_or_exception()

    eave_response = await team.GetTeamRequest.perform(
        origin=MARKETING_APP_CONFIG.eave_origin,
        team_id=unwrap(auth_cookies.team_id),
        account_id=ensure_uuid(auth_cookies.account_id),
        access_token=unwrap(auth_cookies.access_token),
    )

    return _make_response(eave_response)


@app.route("/embed/metabase", methods=["GET"])
@_auth_handler
async def embed_metabase() -> Response:
    auth_cookies = _get_auth_cookies_or_exception()

    resp = await MetabaseEmbeddingSSOOperation.perform(
        input=MetabaseEmbeddingSSOOperation.RequestBody(return_to=request.args.get("return_to")),
        origin=MARKETING_APP_CONFIG.eave_origin,
        team_id=unwrap(auth_cookies.team_id),
        account_id=ensure_uuid(auth_cookies.account_id),
        access_token=unwrap(auth_cookies.access_token),
    )

    return await _make_redirect_response(eave_response=resp)


@app.route("/dashboard/logout", methods=["GET"])
async def logout() -> BaseResponse:
    response = redirect(location=SHARED_CONFIG.eave_public_www_base, code=302)
    delete_auth_cookies(response=response)
    _delete_login_state_hint_cookie(response=response)
    return response


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path: str) -> Response:
    spa = _render_spa()
    response = make_response(spa)

    # We changed these cookie names; This is a courtesy to the user to clean up their old cookies. This can be removed at any time.
    delete_http_cookie(response=response, key="ev_account_id")
    delete_http_cookie(response=response, key="ev_team_id")
    delete_http_cookie(response=response, key="ev_access_token")
    delete_http_cookie(response=response, key="ev_login_state_hint")
    delete_http_cookie(response=response, key="visitor_id")

    set_tracking_cookies(response=response, request=request)

    auth_cookies = get_auth_cookies(request.cookies)
    if auth_cookies.all_set:
        _set_login_state_hint_cookie(response=response)
    else:
        _delete_login_state_hint_cookie(response=response)

    return response


_EAVE_LOGIN_STATE_HINT_COOKIE_NAME = "ev_login_state_hint.202311"


def _set_login_state_hint_cookie(response: BaseResponse) -> None:
    # This cookie is a HINT to the client whether the user may be logged in.
    # It doesn't actually indicate the logged-in state, but the client can use this cookie to decide if it can skip some API calls, for example.
    # This cookie is set to httponly=False so the client can read it.
    set_http_cookie(response=response, key=_EAVE_LOGIN_STATE_HINT_COOKIE_NAME, value="1", httponly=False)


def _delete_login_state_hint_cookie(response: BaseResponse) -> None:
    delete_http_cookie(response=response, key=_EAVE_LOGIN_STATE_HINT_COOKIE_NAME, httponly=False)


def _get_auth_cookies_or_exception() -> AuthCookies:
    auth_cookies = get_auth_cookies(request.cookies)
    if not auth_cookies.all_set:
        raise werkzeug.exceptions.Unauthorized()

    return auth_cookies


async def _make_redirect_response(eave_response: BaseResponseBody) -> Response:
    assert eave_response.raw_response, "invalid eave response"
    headers = dict(eave_response.raw_response.headers)
    status = eave_response.raw_response.status
    response = Response(
        headers=headers,
        status=status,
    )

    return response


def _make_response(eave_response: BaseResponseBody) -> Response:
    response = _json_response(body=eave_response.json())

    if eave_response.cookies:
        cookies = get_auth_cookies(cookies=eave_response.cookies)
        set_auth_cookies(
            response=response, access_token=cookies.access_token, account_id=cookies.account_id, team_id=cookies.team_id
        )

    return response


def _set_json_response_body(response: Response, body: JsonObject | str) -> Response:
    if not isinstance(body, str):
        body = json.dumps(body)
    response.set_data(body)
    return response


def _json_response(body: JsonObject | str | None) -> Response:
    response = Response(mimetype=MIME_TYPE_JSON)
    if body:
        _set_json_response_body(response, body)
    return response
