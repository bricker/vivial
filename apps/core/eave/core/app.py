import aiohttp.hdrs
import starlette.applications
import starlette.endpoints
from asgiref.typing import ASGI3Application
from starlette.middleware import Middleware
from starlette.routing import Route

import eave.stdlib.time
from eave.core.internal.oauth.google import (
    GOOGLE_OAUTH_AUTHORIZE_PATH,
    GOOGLE_OAUTH_CALLBACK_PATH,
)
from eave.core.public.middleware.authentication import AuthASGIMiddleware
from eave.core.public.requests.data_ingestion import BrowserDataIngestionEndpoint, ServerDataIngestionEndpoint
from eave.core.public.requests.metabase_proxy import MetabaseAuthEndpoint, MetabaseProxyEndpoint, MetabaseProxyRouter
from eave.stdlib import cache, logging
from eave.stdlib.core_api.operations import CoreApiEndpointConfiguration
from eave.stdlib.core_api.operations.account import GetMyAccountRequest
from eave.stdlib.core_api.operations.team import GetMyTeamRequest
from eave.stdlib.core_api.operations.virtual_event import GetMyVirtualEventDetailsRequest, ListMyVirtualEventsRequest
from eave.stdlib.middleware.deny_public_request import DenyPublicRequestASGIMiddleware
from eave.stdlib.middleware.exception_handling import ExceptionHandlingASGIMiddleware
from eave.stdlib.middleware.logging import LoggingASGIMiddleware
from eave.stdlib.middleware.origin import OriginASGIMiddleware
from eave.stdlib.middleware.read_body import ReadBodyASGIMiddleware
from eave.stdlib.middleware.request_integrity import RequestIntegrityASGIMiddleware

from .internal.database import async_engine
from .public.exception_handlers import exception_handlers
from .public.requests import (
    authed_account,
    noop,
    status,
    team,
    virtual_event,
)
from .public.requests.oauth import google_oauth

eave.stdlib.time.set_utc()


def make_route(
    config: CoreApiEndpointConfiguration,
    endpoint: ASGI3Application,
    addl_methods: list[str] | None = None,
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
    It's important to remember that a Middleware is just a Callable object that takes ASGI-specific arguments.
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

    - Why not just define them in order and then reverse them? Because these middlewares aren't necessarily all initialized in the same way.

    - Why not use Starlette(middlewares=...) or Route(middlewares...)? Because the starlette Middleware type is too restrictive:
        - The passed-in class must have an initializer with `app: starlette.types.ASGIApp`, but our middlewares accept the more generic `app: asgiref.typing.ASGI3Application`.
          Those two types are compatible but unrelated types, so the typechecker doesn't allow it.
        - The passed-in class can't accept any additional parameters, which is sometimes necessary for our middlewares.
    """

    # When deciding the order of middlewares, start at the _bottom_ of this block and go up.
    # The first middleware, starting from here (the top), directly wraps the route handler.
    # Then, each one wraps the previous one.
    if config.auth_required:
        endpoint = AuthASGIMiddleware(app=endpoint)

    if config.origin_required:
        endpoint = OriginASGIMiddleware(
            app=endpoint,
        )

    endpoint = ReadBodyASGIMiddleware(app=endpoint)

    if not config.is_public:
        endpoint = DenyPublicRequestASGIMiddleware(app=endpoint)

    endpoint = LoggingASGIMiddleware(app=endpoint)
    endpoint = RequestIntegrityASGIMiddleware(app=endpoint)
    endpoint = ExceptionHandlingASGIMiddleware(
        app=endpoint
    )  # This wraps everything and is the first middleware that gets called.

    # ^^ When deciding the order of middlewares, start here and go up ^^

    # This is to append the additional methods, removing any duplicate of config.method, and putting config.method at the beginning.
    addl_methods = [m for m in addl_methods if m != config.method] if addl_methods else []
    return Route(path=config.path, methods=[config.method, *addl_methods], endpoint=endpoint)


routes = [
    ##
    ## Public Endpoints
    ##
    Route(
        path="/status",
        endpoint=status.StatusEndpoint,
        methods=[
            aiohttp.hdrs.METH_GET,
            aiohttp.hdrs.METH_POST,
            aiohttp.hdrs.METH_PUT,
            aiohttp.hdrs.METH_PATCH,
            aiohttp.hdrs.METH_DELETE,
            aiohttp.hdrs.METH_HEAD,
            aiohttp.hdrs.METH_OPTIONS,
        ],
    ),
    Route(
        path="/healthz",
        endpoint=status.HealthEndpoint,
        methods=[aiohttp.hdrs.METH_GET],
    ),
    make_route(
        config=CoreApiEndpointConfiguration(
            path="/public/ingest/server",
            method=aiohttp.hdrs.METH_POST,
            auth_required=False,
            origin_required=False,
            is_public=True,
        ),
        endpoint=ServerDataIngestionEndpoint,
    ),
    make_route(
        config=CoreApiEndpointConfiguration(
            path="/public/ingest/browser",
            method=aiohttp.hdrs.METH_POST,
            auth_required=False,
            origin_required=False,
            is_public=True,
        ),
        endpoint=BrowserDataIngestionEndpoint,
    ),
    make_route(
        config=CoreApiEndpointConfiguration(
            path="/_/metabase/proxy/auth/sso",
            method=aiohttp.hdrs.METH_GET,
            auth_required=True,
            origin_required=False,
            is_public=True,  # This is True because embed.eave.fyi forwards to this endpoint via the LB, which sets the eave-lb header.
        ),
        endpoint=MetabaseAuthEndpoint,
    ),
    make_route(
        config=CoreApiEndpointConfiguration(
            path="/_/metabase/proxy/{rest:path}",
            method=aiohttp.hdrs.METH_GET,
            auth_required=True,
            origin_required=False,
            is_public=True,  # This is True because embed.eave.fyi forwards to this endpoint via the LB, which sets the eave-lb header.
        ),
        endpoint=MetabaseProxyEndpoint,
        addl_methods=[
            aiohttp.hdrs.METH_POST,
            aiohttp.hdrs.METH_PUT,
            aiohttp.hdrs.METH_PATCH,
            aiohttp.hdrs.METH_DELETE,
            aiohttp.hdrs.METH_HEAD,
            aiohttp.hdrs.METH_OPTIONS,
        ],
    ),
    make_route(
        config=CoreApiEndpointConfiguration(
            path=GOOGLE_OAUTH_AUTHORIZE_PATH,
            method=aiohttp.hdrs.METH_GET,
            auth_required=False,
            origin_required=False,
            is_public=True,
        ),
        endpoint=google_oauth.GoogleOAuthAuthorize,
    ),
    make_route(
        config=CoreApiEndpointConfiguration(
            path=GOOGLE_OAUTH_CALLBACK_PATH,
            method=aiohttp.hdrs.METH_GET,
            auth_required=False,
            origin_required=False,
            is_public=True,
        ),
        endpoint=google_oauth.GoogleOAuthCallback,
    ),
    make_route(
        config=CoreApiEndpointConfiguration(
            path="/favicon.ico",
            method=aiohttp.hdrs.METH_GET,
            auth_required=False,
            origin_required=False,
            is_public=True,
        ),
        endpoint=noop.NoopEndpoint,
    ),
    ##
    ## Internal Endpoints
    ##
    make_route(
        config=GetMyTeamRequest.config,
        endpoint=team.GetMyTeamEndpoint,
    ),
    make_route(
        config=ListMyVirtualEventsRequest.config,
        endpoint=virtual_event.ListMyVirtualEventsEndpoint,
    ),
    make_route(
        config=GetMyVirtualEventDetailsRequest.config,
        endpoint=virtual_event.GetMyVirtualEventDetailsEndpoint,
    ),
    make_route(
        config=GetMyAccountRequest.config,
        endpoint=authed_account.GetMyAccountEndpoint,
    ),
]


async def graceful_shutdown() -> None:
    await async_engine.dispose()

    try:
        if client := cache.initialized_client():
            await client.close()
    except Exception as e:
        logging.eaveLogger.exception(e)


app = starlette.applications.Starlette(
    routes=routes,
    exception_handlers=exception_handlers,
    middleware=[Middleware(MetabaseProxyRouter)],
    on_shutdown=[graceful_shutdown],
)
