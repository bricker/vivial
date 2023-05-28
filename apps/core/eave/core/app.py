from eave.core.public.middlewares.body_parser import BodyParserASGIMiddleware
from eave.core.public.requests.atlassian_integration import AtlassianIntegration
import eave.stdlib
import eave.stdlib.api_util
import eave.stdlib.core_api.operations.base
import eave.stdlib.logging
import eave.stdlib.time
import eave.stdlib.core_api.operations as eave_ops
import eave.stdlib.core_api.operations.forge as forge_ops
import starlette.applications
import starlette.endpoints
from asgiref.typing import ASGI3Application
from starlette.middleware import Middleware
from starlette.routing import Route

import eave.core.public.requests.forge_integration
import eave.core.public.requests.github_integration

from .public import middlewares
from .public.exception_handlers import exception_handlers
from .public.requests import authed_account, documents, noop, slack_integration, subscriptions, team, status
from .public.requests.oauth import atlassian_oauth, github_oauth, google_oauth, slack_oauth

eave.stdlib.time.set_utc()


def make_route(
    config: eave.stdlib.core_api.operations.base.EndpointConfiguration,
    endpoint: ASGI3Application,
) -> Route:
    """
    Defines basic information about the route, passed-through to the Starlette router.
    More importantly, defines which headers are required and validated for this route.
    By default, all headers are required. This is an attempt to prevent a developer error from bypassing security mechanisms.
    """

    if config.origin_required:
        endpoint = middlewares.OriginASGIMiddleware(app=endpoint)

    if config.signature_required:
        # If signature is required, origin is also required.
        assert config.origin_required
        endpoint = middlewares.SignatureVerificationASGIMiddleware(app=endpoint)

    if config.auth_required:
        endpoint = middlewares.AuthASGIMiddleware(app=endpoint)

    if config.team_id_required:
        endpoint = middlewares.TeamLookupASGIMiddleware(app=endpoint)

    return Route(path=config.path, endpoint=endpoint)



routes = [
    Route(path="/status", endpoint=status.StatusRequest, methods=["GET", "POST", "DELETE", "HEAD", "OPTIONS"]),
    Route(path="/_ah/warmup", endpoint=status.WarmupRequest, methods=["GET"]),
    # Internal API Endpoints.
    # These endpoints require signature verification.
    make_route(
        config=eave_ops.UpsertDocument.config,
        endpoint=documents.UpsertDocument,
    ),
    make_route(
        config=eave_ops.SearchDocuments.config,
        endpoint=documents.SearchDocuments,
    ),
    make_route(
        config=eave_ops.DeleteDocument.config,
        endpoint=documents.DeleteDocument,
    ),
    make_route(
        config=eave_ops.CreateSubscription.config,
        endpoint=subscriptions.CreateSubscription,
    ),
    make_route(
        config=eave_ops.GetSubscription.config,
        endpoint=subscriptions.GetSubscription,
    ),
    make_route(
        config=eave_ops.DeleteSubscription.config,
        endpoint=subscriptions.DeleteSubscription,
    ),
    make_route(
        config=eave_ops.GetSlackInstallation.config,
        endpoint=slack_integration.SlackIntegration,
    ),
    make_route(
        config=eave_ops.GetGithubInstallation.config,
        endpoint=eave.core.public.requests.github_integration.GithubIntegration,
    ),
    make_route(
        config=eave_ops.GetAtlassianInstallation.config,
        endpoint=AtlassianIntegration,
    ),
    make_route(
        config=forge_ops.QueryForgeInstallation.config,
        endpoint=eave.core.public.requests.forge_integration.QueryForgeIntegration,
    ),
    make_route(
        config=forge_ops.RegisterForgeInstallation.config,
        endpoint=eave.core.public.requests.forge_integration.RegisterForgeIntegration,
    ),
    make_route(
        config=forge_ops.UpdateForgeInstallation.config,
        endpoint=eave.core.public.requests.forge_integration.UpdateForgeIntegration,
    ),
    make_route(
        config=eave.stdlib.core_api.operations.base.EndpointConfiguration(
            path=f"/me/team/{eave_ops.UpdateAtlassianInstallation.config.path}",
            team_id_required=False,
        ),
        endpoint=authed_account.UpdateAtlassianIntegration,
    ),
    make_route(
        config=eave.stdlib.core_api.operations.base.EndpointConfiguration(
            path=f"/me/team/{forge_ops.UpdateForgeInstallation.config.path}",
            team_id_required=False,
        ),
        endpoint=eave.core.public.requests.forge_integration.UpdateForgeIntegration, # TODO: This can be shared with the one in 'integrations'
    ),
    make_route(
        config=eave_ops.GetTeam.config,
        endpoint=team.GetTeam,
    ),
    # Authenticated API endpoints.
    make_route(
        config=eave_ops.GetAuthenticatedAccount.config,
        endpoint=authed_account.GetAuthedAccount,
    ),
    make_route(
        config=eave_ops.GetAuthenticatedAccountTeamIntegrations.config,
        endpoint=authed_account.GetAuthedAccountTeamIntegrations,
    ),
    # OAuth endpoints.
    # These endpoints don't require any verification (except the OAuth flow itself)
    make_route(
        config=eave.stdlib.core_api.operations.base.EndpointConfiguration(
            path="/oauth/google/authorize",
            auth_required=False,
            signature_required=False,
            origin_required=False,
            team_id_required=False,
        ),
        endpoint=google_oauth.GoogleOAuthAuthorize,
    ),
    make_route(
        config=eave.stdlib.core_api.operations.base.EndpointConfiguration(
            path="/oauth/google/callback",
            auth_required=False,
            signature_required=False,
            origin_required=False,
            team_id_required=False,
        ),
        endpoint=google_oauth.GoogleOAuthCallback,
    ),
    make_route(
        config=eave.stdlib.core_api.operations.base.EndpointConfiguration(
            path="/oauth/slack/authorize",
            auth_required=False,
            signature_required=False,
            origin_required=False,
            team_id_required=False,
        ),
        endpoint=slack_oauth.SlackOAuthAuthorize,
    ),
    make_route(
        config=eave.stdlib.core_api.operations.base.EndpointConfiguration(
            path="/oauth/slack/callback",
            auth_required=False,
            signature_required=False,
            origin_required=False,
            team_id_required=False,
        ),
        endpoint=slack_oauth.SlackOAuthCallback,
    ),
    make_route(
        config=eave.stdlib.core_api.operations.base.EndpointConfiguration(
            path="/oauth/atlassian/authorize",
            auth_required=False,
            signature_required=False,
            origin_required=False,
            team_id_required=False,
        ),
        endpoint=atlassian_oauth.AtlassianOAuthAuthorize,
    ),
    make_route(
        config=eave.stdlib.core_api.operations.base.EndpointConfiguration(
            path="/oauth/atlassian/callback",
            auth_required=False,
            signature_required=False,
            origin_required=False,
            team_id_required=False,
        ),
        endpoint=atlassian_oauth.AtlassianOAuthCallback,
    ),
    make_route(
        config=eave.stdlib.core_api.operations.base.EndpointConfiguration(
            path="/oauth/github/authorize",
            auth_required=False,
            signature_required=False,
            origin_required=False,
            team_id_required=False,
        ),
        endpoint=github_oauth.GithubOAuthAuthorize,
    ),
    make_route(
        config=eave.stdlib.core_api.operations.base.EndpointConfiguration(
            path="/oauth/github/callback",
            auth_required=False,
            signature_required=False,
            origin_required=False,
            team_id_required=False,
        ),
        endpoint=github_oauth.GithubOAuthCallback,
    ),
    make_route(
        config=eave.stdlib.core_api.operations.base.EndpointConfiguration(
            path="/favicon.ico",
            auth_required=False,
            signature_required=False,
            origin_required=False,
            team_id_required=False,
        ),
        endpoint=noop.NoopRequest,
    ),
]

middleware = [
    Middleware(middlewares.RequestIntegrityASGIMiddleware),
    Middleware(BodyParserASGIMiddleware),
    Middleware(middlewares.LoggingASGIMiddleware),
]

app = starlette.applications.Starlette(
    middleware=middleware,
    routes=routes,
    exception_handlers=exception_handlers,
)
