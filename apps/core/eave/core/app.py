from eave.core.public.middlewares.body_parser import BodyParserASGIMiddleware
from eave.core.public.requests.atlassian_integration import AtlassianIntegration
import eave.stdlib
import eave.stdlib.api_util
import eave.stdlib.core_api.operations.base
import eave.stdlib.core_api.operations.integrations
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

    """
    The order of these is important! Inner middlewares may have dependencies on outer middlewares.
    The middlewares are ordered here from "inner" to "outer".
    Although we are _initializing_ the middlewares here, we're not _calling_ them.
    It's important to remember that a Middleware is just a Callable object that takes ASGI specific arguments.
    When we "initialize" a Middleware, we're really just creating a pre-configured Callable.
    It is common to have a Middleware that isn't initialized in this way, and instead a class itself is provided as the Callable.
    In that case, the class's initializer would take the necessary ASGI arguments.

    Consider that for most of these middlewares, the procedure goes something like this:

        1. Middleware (i.e. Callable) is called and given the current request
        1. Middleware modifies the request in some way
        1. Middleware calls the next middleware in the chain, passing the modified request

    With that in mind, consider this example middleware chain:

        1. RequestLoggerMiddleware   # A callable that receives the request and logs the information
        1. BodyParserMiddleware      # A callable that receives the request, parses the body, and attaches the parsed body to the request object
        1. BodyValidationMiddleware  # A callable that receives the request (with the parsed body attached) and validates the data in the body

    This middleware chain should be created like this, _seemingly_ in reverse order:

        endpoint = MyRouteHandler()
        endpoint = BodyValidationMiddleware(app=endpoint)
        endpoint = BodyParserMiddleware(app=endpoint)
        endpoint = RequestLoggerMiddleware(app=endpoint) # < This is the final "endpoint" that gets called by the ASGI server

    BodyValidationMiddleware directly wraps MyRouteHandler, because the validation is the _last_ thing that happens before the route handler runs.
    Similarly, BodyParserMiddleware wraps BodyValidationMiddleware, because the body needs to be parsed before it can be validated.
    And finally, the RequstLoggerMiddleware wraps everything, because it should log the request information before anything else happens.

    Internally, the Middlewares do their work and then hand off the request to the next middleware.
    Although a Middleware is just a Callable, in most cases it needs to be an instance of a class so that it has a reference to the next middleware.
    Often this is an object called "app" attached to the instance.
    In these examples the name "next" is used to help with understanding, but is a reserved keyword in Python so not commonly used.

    Here's what the initialization for the above middleware chain would look like if done all in one call:

        ASGI(
            next = RequestLoggerMiddleware(
                next = BodyParserMiddleware(
                    next = BodyValidationMiddleware(
                        next = MyRouteHandler
        ))))

    Note that MyRouteHandler is not an instance in this example, because it is the last Callable in the chain and
    doesn't need a reference to any other callables.

    The classes might look like this (arguments are simplified for this example)

        class ASGI:
            next: RequestLoggerMiddleware
            def __call__(self, request):
                self.next(request)

        class RequestLoggerMiddleware:
            next: BodyParserMiddleware
            def __call__(self, request):
                logger.log('received request')
                self.next(request)

        class BodyParserMiddleware:
            next: BodyValidationMiddleware
            def __call__(self, request):
                parsed_body = json.loads(request.body)
                request.state.parsed_body = parsed_body
                self.next(request)

        class BodyValidationMiddleware:
            next: MyRouteHandler
            def __call__(self, request):
                parsed_body = request.state.parsed_body
                assert parsed_body["name"] is not None, "Name is required"
                self.next(request)

        class MyRouteHandler:
            def __init__(self, request):
                parsed_body = request.state.parsed_body
                save_to_database(parsed_body)
                return Response(status_code=200)

    So, that's a long-winded explanation of the order of the middlewares below.
    """

    if config.team_id_required:
        # Last thing to happen before the Route handler
        endpoint = middlewares.TeamLookupASGIMiddleware(app=endpoint)

    if config.auth_required:
        endpoint = middlewares.AuthASGIMiddleware(app=endpoint)

    if config.signature_required:
        # If signature is required, origin is also required.
        assert config.origin_required
        endpoint = middlewares.SignatureVerificationASGIMiddleware(app=endpoint)

    if config.origin_required:
        # First thing to happen when the middleware chain is kicked off
        endpoint = middlewares.OriginASGIMiddleware(app=endpoint)

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
        config=eave.stdlib.core_api.operations.integrations.GetSlackInstallation.config,
        endpoint=slack_integration.SlackIntegration,
    ),
    make_route(
        config=eave.stdlib.core_api.operations.integrations.GetGithubInstallation.config,
        endpoint=eave.core.public.requests.github_integration.GithubIntegration,
    ),
    make_route(
        config=eave.stdlib.core_api.operations.integrations.GetAtlassianInstallation.config,
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
            path=f"/me/team/{eave.stdlib.core_api.operations.integrations.UpdateAtlassianInstallation.config.path}",
            team_id_required=False,
        ),
        endpoint=authed_account.UpdateAtlassianIntegration,
    ),
    make_route(
        config=eave.stdlib.core_api.operations.base.EndpointConfiguration(
            path=f"/me/team/{forge_ops.UpdateForgeInstallation.config.path}",
            team_id_required=False,
        ),
        endpoint=eave.core.public.requests.forge_integration.UpdateForgeIntegration,  # TODO: This can be shared with the one in 'integrations'
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
