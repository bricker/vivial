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
from eave.stdlib.auth_cookies import delete_auth_cookies
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.core_api.operations.status import status_payload
from eave.stdlib.headers import MIME_TYPE_JSON
from eave.stdlib.utm_cookies import set_tracking_cookies

from .config import DASHBOARD_APP_CONFIG

eave.stdlib.time.set_utc()


# def _auth_handler(f: Callable[[Request, AuthCookies], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]:
#     @wraps(f)
#     async def wrapper(request: Request) -> Response:
#         try:
#             auth_cookies = _get_auth_cookies_or_exception(request=request)
#             r = await f(request, auth_cookies)
#             return r
#         except (ClientResponseError, UnauthorizedError) as e:
#             if e.code == HTTPStatus.UNAUTHORIZED:
#                 response = Response(status_code=HTTPStatus.UNAUTHORIZED)
#                 delete_auth_cookies(request=request, response=response)
#                 return response
#             else:
#                 raise

#     return wrapper


def status_endpoint(request: Request) -> Response:
    model = status_payload()
    response = Response(content=model.json(), status_code=HTTPStatus.OK, media_type=MIME_TYPE_JSON)
    return response


def health_endpoint(request: Request) -> Response:
    return Response(content="1", status_code=HTTPStatus.OK)


# @_auth_handler
# async def validate_user_auth_endpoint(request: Request, auth_cookies: AuthCookies) -> Response:
#     await GetMyAccountRequest.perform(
#         origin=DASHBOARD_APP_CONFIG.eave_origin,
#         account_id=unwrap(auth_cookies.account_id),
#         access_token=unwrap(auth_cookies.access_token),
#     )

#     return Response(status_code=200)


# @_auth_handler
# async def get_virtual_events_endpoint(request: Request, auth_cookies: AuthCookies) -> Response:
#     body = await request.json()
#     query: str | None = body.get("query")

#     eave_response = await virtual_event.ListMyVirtualEventsRequest.perform(
#         origin=DASHBOARD_APP_CONFIG.eave_origin,
#         account_id=unwrap(auth_cookies.account_id),
#         access_token=unwrap(auth_cookies.access_token),
#         input=virtual_event.ListMyVirtualEventsRequest.RequestBody(query=query),
#     )

#     return _make_response(eave_response)

# @_auth_handler
# async def get_virtual_event_details_endpoint(request: Request, auth_cookies: AuthCookies) -> Response:
#     body = await request.json()
#     vevent_id: str | None = body.get("id")
#     if vevent_id is None:
#         raise BadRequestError()

#     eave_response = await virtual_event.GetMyVirtualEventDetailsRequest.perform(
#         origin=DASHBOARD_APP_CONFIG.eave_origin,
#         account_id=unwrap(auth_cookies.account_id),
#         access_token=unwrap(auth_cookies.access_token),
#         input=virtual_event.GetMyVirtualEventDetailsRequest.RequestBody(
#             virtual_event=VirtualEventDetailsQueryInput(
#                 id=ensure_uuid(vevent_id),
#             ),
#         ),
#     )

#     return _make_response(eave_response)


# @_auth_handler
# async def get_team_endpoint(request: Request, auth_cookies: AuthCookies) -> Response
#     eave_response = await team.GetMyTeamRequest.perform(
#         origin=DASHBOARD_APP_CONFIG.eave_origin,
#         account_id=unwrap(auth_cookies.account_id),
#         access_token=unwrap(auth_cookies.access_token),
#     )

#     return _make_response(eave_response)


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

    set_tracking_cookies(response=response, request=request)
    return response


# def _get_auth_cookies_or_exception(request: Request) -> AuthCookies:
#     auth_cookies = get_auth_cookies(request.cookies)
#     if not auth_cookies.all_set:
#         raise UnauthorizedError()

#     return auth_cookies


# def _make_response(eave_response: BaseResponseBody) -> Response:
#     # JSONResponse would automatically serialize the passed-in data, but the data may not be readily serializable.
#     # Instead, we rely on Pydantic's `.json()` function to safely serialize the model.
#     response = Response(media_type=MIME_TYPE_JSON, content=eave_response.json())

#     if eave_response.cookies:
#         cookies = get_auth_cookies(cookies=eave_response.cookies)
#         set_auth_cookies(
#             response=response,
#             access_token=cookies.access_token,
#             account_id=cookies.account_id,
#         )

#     return response


app = Starlette(
    routes=[
        Mount("/static", StaticFiles(directory="eave/dashboard/static")),
        Route(
            path="/status",
            methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
            endpoint=status_endpoint,
        ),
        Route(path="/healthz", methods=["GET"], endpoint=health_endpoint),
        # Route(path="/api/auth", methods=["GET"], endpoint=validate_user_auth_endpoint),
        # Route(path="/api/team/virtual-events", methods=["POST"], endpoint=get_virtual_events_endpoint),
        # Route(path="/api/team", methods=["POST"], endpoint=get_team_endpoint),
        Route(path="/logout", methods=["GET"], endpoint=logout_endpoint),
        Route(path="/{rest:path}", methods=["GET"], endpoint=web_app_endpoint),
    ],
)
