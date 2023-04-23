from typing import Any, Callable
import eave.stdlib.api_util
import eave.stdlib.logging
import fastapi

from .public.requests import (
    access_requests,
    authed_account,
    documents,
    slack_installations,
    subscriptions,
    auth,
)
from .public.requests import util as eave_request_util
from .public.requests.oauth_handlers import atlassian_oauth, google_oauth, slack_oauth
from .public.middlewares import (
    auth_middleware,
    validate_signature_middleware,
    origin_middleware,
    team_lookup_middleware,
    request_id_middleware,
)

eave.stdlib.logging.setup_logging()

app = fastapi.FastAPI()

eave.stdlib.api_util.add_standard_endpoints(app=app)
eave_request_util.add_standard_exception_handlers(app=app)

validate_signature_middleware.add_bypass("/status")
auth_middleware.add_bypass("/status")

app.add_middleware(request_id_middleware.RequestIdMiddleware)
app.add_middleware(origin_middleware.OriginMiddleware)
app.add_middleware(validate_signature_middleware.ValidateSignatureMiddleware)
app.add_middleware(auth_middleware.AuthMiddleware)
app.add_middleware(team_lookup_middleware.TeamLookupMiddleware)

def add_route(
        method: str,
        path: str,
        handler: Any,
        signature_required: bool = True,
        auth_required: bool = True,
        origin_required: bool = True,
        team_id_required: bool = True,
    ) -> None:
    """
    Defines basic information about the route, passed-through to the FastAPI router.
    More importantly, defines which headers are required and validated for this route.
    By default, all headers are required. This is an attempt to prevent a developer error from bypassing security mechanisms.
    """
    if not signature_required:
        validate_signature_middleware.add_bypass(path)

    if not auth_required:
        auth_middleware.add_bypass(path)

    if not origin_required:
        origin_middleware.add_bypass(path)

    if not team_id_required:
        team_lookup_middleware.add_bypass(path)

    app.add_api_route(
        path=path,
        endpoint=handler,
        methods=[method],
    )

# Internal API Endpoints.
# These endpoints require signature verification.
add_route(method="POST", path="/access_request",            auth_required=False, signature_required=True, origin_required=True, team_id_required=False, handler=access_requests.create_access_request)
add_route(method="POST", path="/documents/upsert",          auth_required=False, signature_required=True, origin_required=True, team_id_required=True, handler=documents.upsert_document)
add_route(method="POST", path="/subscriptions/create",      auth_required=False, signature_required=True, origin_required=True, team_id_required=True, handler=subscriptions.create_subscription)
add_route(method="POST", path="/subscriptions/query",       auth_required=False, signature_required=True, origin_required=True, team_id_required=True, handler=subscriptions.get_subscription)
add_route(method="POST", path="/subscriptions/delete",      auth_required=False, signature_required=True, origin_required=True, team_id_required=True, handler=subscriptions.delete_subscription)
add_route(method="POST", path="/installations/slack/query", auth_required=False, signature_required=True, origin_required=True, team_id_required=True, handler=slack_installations.query)

# Auth Token endpoints
add_route(method="POST", path="/auth/token/request", auth_required=False, signature_required=True, origin_required=True, team_id_required=False, handler=auth.request_access_token)
add_route(method="POST", path="/auth/token/refresh", auth_required=True, signature_required=True, origin_required=True, team_id_required=False, handler=auth.refresh_access_token)

# Authenticated API endpoints.
# These endpoints require both signature verification and auth token verification.
# add_route(method="POST", path="/me/account",            auth_required=True, signature_required=True, origin_required=True, team_id_required=True, handler=authed_account.get_current_account)
# add_route(method="POST", path="/me/team",               auth_required=True, signature_required=True, origin_required=True, team_id_required=True, handler=authed_account.get_current_team)
# add_route(method="POST", path="/me/team/installations", auth_required=True, signature_required=True, origin_required=True, team_id_required=True, handler=authed_account.get_installations)

# OAuth endpoints.
# These endpoints don't require any verification (except the OAuth flow itself)
add_route(method="GET", path="/oauth/google/authorize",     auth_required=False, signature_required=False, origin_required=False, team_id_required=False, handler=google_oauth.google_oauth_authorize)
add_route(method="GET", path="/oauth/google/callback",      auth_required=False, signature_required=False, origin_required=False, team_id_required=False, handler=google_oauth.google_oauth_callback)
add_route(method="GET", path="/oauth/slack/authorize",      auth_required=False, signature_required=False, origin_required=False, team_id_required=False, handler=slack_oauth.slack_oauth_authorize)
add_route(method="GET", path="/oauth/slack/callback",       auth_required=False, signature_required=False, origin_required=False, team_id_required=False, handler=slack_oauth.slack_oauth_callback)
add_route(method="GET", path="/oauth/atlassian/authorize",  auth_required=False, signature_required=False, origin_required=False, team_id_required=False, handler=atlassian_oauth.atlassian_oauth_authorize)
add_route(method="GET", path="/oauth/atlassian/callback",   auth_required=False, signature_required=False, origin_required=False, team_id_required=False, handler=atlassian_oauth.atlassian_oauth_callback)
