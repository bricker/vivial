from functools import reduce
from typing import Type
import eave.stdlib
import eave.stdlib.api_util
import eave.stdlib.logging
import eave.stdlib.time
import starlette.applications
import starlette.endpoints
from asgiref.typing import ASGI3Application
from starlette.middleware import Middleware
from starlette.routing import Route

from eave.stdlib.middleware.base import EaveASGIMiddleware
from .public import middlewares
from .public.exception_handlers import exception_handlers
from .public.requests import authed_account, documents, integrations, noop, subscriptions, team, status
from .public.requests.oauth_handlers import atlassian_oauth, github_oauth, google_oauth, slack_oauth

eave.stdlib.time.set_utc()


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
    """

    # The middlewares in this list should be ordered starting with the outermost middleware first.
    # The outermost middleware is the middleware that will be run first on the request, and last on the response.
    #
    # Example:
    #   wrappers = [ OuterMost, Second, InnerMost ]
    #
    # The built route ends up being called like this:
    #   route = OuterMost(Second(InnerMost(endpoint)))

    out_to_in_wrappers: list[Type[EaveASGIMiddleware]] = []

    if origin_required:
        out_to_in_wrappers.append(middlewares.OriginASGIMiddleware)

    if signature_required:
        # If signature is required, origin is also required.
        assert origin_required, "origin header is required for signature"
        out_to_in_wrappers.append(middlewares.SignatureVerificationASGIMiddleware)

    if auth_required:
        out_to_in_wrappers.append(middlewares.AuthASGIMiddleware)

    if team_id_required:
        out_to_in_wrappers.append(middlewares.TeamLookupASGIMiddleware)

    # The middlewares list needs to be reversed before initializing because of the call stack.
    # Reversing the middlewares is the same as doing this:
    #   route = InnerMost(endpoint)
    #   route = Second(route)
    #   route = OuterMost(route)
    # Which is the same as:
    #   route = OuterMost(Second(InnerMost(endpoint)))
    wrapped_endpoint = reduce(lambda acc, v: v(app=acc), reversed(out_to_in_wrappers), endpoint)
    return Route(path=path, endpoint=wrapped_endpoint)


routes = [
    Route(path="/status", endpoint=status.StatusRequest),
    Route(path="/_ah/warmup", endpoint=status.WarmupRequest, methods=["GET"]),
    # Internal API Endpoints.
    # These endpoints require signature verification.
    make_route(
        path="/documents/upsert",
        auth_required=False,
        endpoint=documents.UpsertDocument,
    ),
    make_route(
        path="/documents/search",
        auth_required=False,
        endpoint=documents.SearchDocuments,
    ),
    make_route(
        path="/documents/delete",
        auth_required=False,
        endpoint=documents.DeleteDocument,
    ),
    make_route(
        path="/subscriptions/create",
        auth_required=False,
        endpoint=subscriptions.CreateSubscription,
    ),
    make_route(
        path="/subscriptions/query",
        auth_required=False,
        endpoint=subscriptions.GetSubscription,
    ),
    make_route(
        path="/subscriptions/delete",
        auth_required=False,
        endpoint=subscriptions.DeleteSubscription,
    ),
    make_route(
        path="/integrations/slack/query",
        auth_required=False,
        team_id_required=False,
        endpoint=integrations.SlackIntegration,
    ),
    make_route(
        path="/integrations/github/query",
        auth_required=False,
        team_id_required=False,
        endpoint=integrations.GithubIntegration,
    ),
    make_route(
        path="/integrations/atlassian/query",
        auth_required=False,
        team_id_required=False,
        endpoint=integrations.AtlassianIntegration,
    ),
    make_route(
        path="/team/query",
        auth_required=False,
        endpoint=team.GetTeam,
    ),
    # Authenticated API endpoints.
    make_route(
        path="/me/query",
        team_id_required=False,
        endpoint=authed_account.GetAuthedAccount,
    ),
    make_route(
        path="/me/team/integrations/query",
        team_id_required=False,
        endpoint=authed_account.GetAuthedAccountTeamIntegrations,
    ),
    make_route(
        path="/me/team/integrations/atlassian/update",
        team_id_required=False,
        endpoint=authed_account.UpdateAtlassianIntegration,
    ),
    # OAuth endpoints.
    # These endpoints don't require any verification (except the OAuth flow itself)
    make_route(
        path="/oauth/google/authorize",
        auth_required=False,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
        endpoint=google_oauth.GoogleOAuthAuthorize,
    ),
    make_route(
        path="/oauth/google/callback",
        auth_required=False,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
        endpoint=google_oauth.GoogleOAuthCallback,
    ),
    make_route(
        path="/oauth/slack/authorize",
        auth_required=False,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
        endpoint=slack_oauth.SlackOAuthAuthorize,
    ),
    make_route(
        path="/oauth/slack/callback",
        auth_required=False,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
        endpoint=slack_oauth.SlackOAuthCallback,
    ),
    make_route(
        path="/oauth/atlassian/authorize",
        auth_required=False,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
        endpoint=atlassian_oauth.AtlassianOAuthAuthorize,
    ),
    make_route(
        path="/oauth/atlassian/callback",
        auth_required=False,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
        endpoint=atlassian_oauth.AtlassianOAuthCallback,
    ),
    make_route(
        path="/oauth/github/authorize",
        auth_required=False,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
        endpoint=github_oauth.GithubOAuthAuthorize,
    ),
    make_route(
        path="/oauth/github/callback",
        auth_required=False,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
        endpoint=github_oauth.GithubOAuthCallback,
    ),
    make_route(
        path="/favicon.ico",
        auth_required=False,
        signature_required=False,
        origin_required=False,
        team_id_required=False,
        endpoint=noop.NoopRequest,
    ),
]

middleware = [
    Middleware(middlewares.RequestIntegrityASGIMiddleware),
    Middleware(middlewares.LoggingASGIMiddleware),
]

app = starlette.applications.Starlette(
    middleware=middleware,
    routes=routes,
    exception_handlers=exception_handlers,
)
