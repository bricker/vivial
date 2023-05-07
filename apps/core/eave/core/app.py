from typing import Any, Type, cast

import eave.stdlib.api_util
import eave.stdlib.logging
import eave.stdlib.time
import starlette.applications
import starlette.endpoints
from starlette.middleware import Middleware
from starlette.routing import Route
from asgiref.typing import ASGI3Application
from .public import middlewares

from .public.requests import (
    authed_account,
    documents,
    integrations,
    subscriptions,
    team,
)
from .public.requests.oauth_handlers import atlassian_oauth, google_oauth, slack_oauth, github_oauth
from .public.exception_handlers import exception_handlers

eave.stdlib.time.set_utc()
eave.stdlib.logging.setup_logging()


def make_route(
    path: str,
    endpoint: ASGI3Application,
    signature_required: bool = True,
    auth_required: bool = True,
    origin_required: bool = True,
    team_id_required: bool = True,
) -> Route:
    """
    Defines basic information about the route, passed-through to the Starlette router.
    More importantly, defines which headers are required and validated for this route.
    By default, all headers are required. This is an attempt to prevent a developer error from bypassing security mechanisms.
    Note: The order of the middlewares is in REVERSE order.
    """

    route: ASGI3Application = endpoint

    # Last middleware:
    if team_id_required:
        route = middlewares.TeamLookupASGIMiddleware(app=route)

    if auth_required:
        route = middlewares.AuthASGIMiddleware(app=route)

    if origin_required:
        route = middlewares.OriginASGIMiddleware(app=route)

    # First middleware:
    if signature_required:
        # If signature is required, origin is also required.
        assert origin_required
        route = middlewares.SignatureVerificationASGIMiddleware(app=route)

    return Route(path=path, endpoint=route)

routes = [
    *eave.stdlib.api_util.standard_endpoints,

    # Internal API Endpoints.
    # These endpoints require signature verification.
    make_route(
        method="POST",
        path="/access_request",
        auth_required=False,
        signature_required=True,
        origin_required=True,
        team_id_required=False,
        endpoint=access_requests.create_access_request,
    ),
    make_route(
        method="POST",
        path="/documents/upsert",
        auth_required=False,
        signature_required=True,
        origin_required=True,
        team_id_required=True,
        endpoint=documents.upsert_document,
    ),
    make_route(
        method="POST",
        path="/subscriptions/create",
        auth_required=False,
        signature_required=True,
        origin_required=True,
        team_id_required=True,
        endpoint=subscriptions.create_subscription,
    ),
    make_route(
        method="POST",
        path="/subscriptions/query",
        auth_required=False,
        signature_required=True,
        origin_required=True,
        team_id_required=True,
        endpoint=subscriptions.get_subscription,
    ),
    make_route(
        method="POST",
        path="/subscriptions/delete",
        auth_required=False,
        signature_required=True,
        origin_required=True,
        team_id_required=True,
        endpoint=subscriptions.delete_subscription,
    ),

    make_route(
        method="POST",
        path="/integrations/slack/query",
        auth_required=False,
        signature_required=True,
        origin_required=True,
        team_id_required=False,
        endpoint=integrations.slack,
    ),

    make_route(
        method="POST",
        path="/integrations/github/query",
        auth_required=False,
        signature_required=True,
        origin_required=True,
        team_id_required=False,
        endpoint=integrations.github,
    ),
    make_route(
        method="POST",
        path="/integrations/atlassian/query",
        auth_required=False,
        signature_required=True,
        origin_required=True,
        team_id_required=False,
        endpoint=integrations.atlassian,
    ),
    make_route(
        method="POST",
        path="/team/query",
        auth_required=False,
        signature_required=True,
        origin_required=True,
        team_id_required=True,
        endpoint=team.get_team,
    ),

    # Authenticated API endpoints.
    make_route(
        method="POST",
        path="/me/query",
        auth_required=True,
        signature_required=True,
        origin_required=True,
        team_id_required=False,
        endpoint=authed_account.get_authed_account,
    ),
    make_route(
        method="POST",
        path="/me/team/integrations/query",
        auth_required=True,
        signature_required=True,
        origin_required=True,
        team_id_required=False,
        endpoint=authed_account.get_authed_account_team_integrations,
    ),
    make_route(
        method="POST",
        path="/me/team/integrations/atlassian/update",
        auth_required=True,
        signature_required=True,
        origin_required=True,
        team_id_required=False,
        endpoint=authed_account.update_atlassian_integration,
    ),


    # OAuth endpoints.
    # These endpoints don't require any verification (except the OAuth flow itself)
    make_route(
        method="GET",
        path="/oauth/google/authorize",
        auth_required=False,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
        endpoint=google_oauth.google_oauth_authorize,
    ),
    make_route(
        method="GET",
        path="/oauth/google/callback",
        auth_required=False,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
        endpoint=google_oauth.google_oauth_callback,
    ),
    make_route(
        method="GET",
        path="/oauth/slack/authorize",
        auth_required=False,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
        endpoint=slack_oauth.slack_oauth_authorize,
    ),
    make_route(
        method="GET",
        path="/oauth/slack/callback",
        auth_required=False,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
        endpoint=slack_oauth.slack_oauth_callback,
    ),
    make_route(
        method="GET",
        path="/oauth/atlassian/authorize",
        auth_required=False,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
        endpoint=atlassian_oauth.atlassian_oauth_authorize,
    ),
    make_route(
        method="GET",
        path="/oauth/atlassian/callback",
        auth_required=False,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
        endpoint=atlassian_oauth.atlassian_oauth_callback,
    ),
    make_route(
        method="GET",
        path="/oauth/github/authorize",
        auth_required=False,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
        endpoint=github_oauth.github_oauth_authorize,
    ),
    make_route(
        method="GET",
        path="/oauth/github/callback",
        auth_required=False,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
        endpoint=github_oauth.github_oauth_callback,
    ),
    make_route(
        method="GET",
        path="/favicon.ico",
        auth_required=False,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
        endpoint=lambda: "",
    )
]

middleware = [
    Middleware(middlewares.ExceptionHandlerASGIMiddleware),
    Middleware(middlewares.RequestIntegrityASGIMiddleware),
]

app = starlette.applications.Starlette(
    middleware=middleware,
    routes=routes,
    exception_handlers=exception_handlers,
)
