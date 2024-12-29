import contextlib
from collections.abc import AsyncGenerator

import aiohttp.hdrs
import starlette.applications
import starlette.endpoints
import stripe
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount, Route
from strawberry.asgi import GraphQL

import eave.stdlib.time
from eave.core.config import CORE_API_APP_CONFIG
from eave.core.endpoints.health import HealthEndpoint
from eave.core.endpoints.logout import LogoutEndpoint
from eave.core.endpoints.noop import NoopEndpoint
from eave.core.endpoints.refresh_tokens import RefreshTokensEndpoint
from eave.core.endpoints.status import StatusEndpoint
from eave.stdlib.starlette import exception_handlers
from eave.stdlib import cache
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER
from eave.stdlib.middleware.iap_jwt_validation import IAPJWTValidationMiddleware

from .admin.graphql.schema import schema as internal_schema
from .database import async_engine
from .graphql.schema import schema

eave.stdlib.time.set_utc()

try:
    stripe.api_key = CORE_API_APP_CONFIG.stripe_secret_key
except Exception as e:
    if SHARED_CONFIG.is_local:
        LOGGER.exception(e)
        LOGGER.warning("Stripe API key not set! Stripe functionality will not work.")
    else:
        # This makes sure that the pod won't start in Kubernetes.
        raise

graphql_app = GraphQL(
    schema=schema,
    allow_queries_via_get=False,
    graphql_ide="graphiql" if SHARED_CONFIG.is_development else None,  # Disable graphiql in production
)


internal_graphql_app = GraphQL(
    schema=internal_schema,
    allow_queries_via_get=False,
    graphql_ide="graphiql" if SHARED_CONFIG.is_development else None,  # Disable graphiql in production
)


@contextlib.asynccontextmanager
async def _app_lifespan(app: starlette.applications.Starlette) -> AsyncGenerator[None, None]:
    if not SHARED_CONFIG.is_local:
        # Preload config in production environments.
        # The idea here is that in development, secrets and required envs
        # should be lazily evaluated, but in production environments
        # we want to attempt to load them before the application starts up,
        # so that it will fail to start if anything required is unavailable.
        SHARED_CONFIG.preload()
        CORE_API_APP_CONFIG.preload()

    yield

    await async_engine.dispose()

    try:
        if client := cache.initialized_client():
            await client.close()
    except Exception as e:
        LOGGER.exception(e)


app = starlette.applications.Starlette(
    routes=[
        Route(
            path="/status",
            endpoint=StatusEndpoint,
            methods=[
                aiohttp.hdrs.METH_GET,
            ],
        ),
        Route(
            path="/healthz",
            endpoint=HealthEndpoint,
            methods=[aiohttp.hdrs.METH_GET],
        ),
        Route(
            path="/favicon.ico",  # TODO: This path should be served from a static source
            endpoint=NoopEndpoint,
            methods=[aiohttp.hdrs.METH_GET],
        ),
        Route(
            path="/graphql",
            methods=[
                aiohttp.hdrs.METH_POST,
                aiohttp.hdrs.METH_GET,  # Allows GraphiQL in development
            ]
            if SHARED_CONFIG.is_development
            else [
                aiohttp.hdrs.METH_POST,
            ],
            endpoint=graphql_app,
        ),
        Route(
            path="/public/logout",
            endpoint=LogoutEndpoint,
            methods=[
                aiohttp.hdrs.METH_GET,
            ],
        ),
        Route(
            path="/public/refresh_tokens",
            endpoint=RefreshTokensEndpoint,
            methods=[
                aiohttp.hdrs.METH_POST,
            ],
        ),
        Mount(
            # This path prefix matches configuration in Kubernetes and shouldn't be changed.
            # It is configured to send everything on this path through the IAP
            "/iap",
            middleware=[Middleware(IAPJWTValidationMiddleware, aud=CORE_API_APP_CONFIG.iap_jwt_aud)],
            routes=[
                Route(
                    path="/graphql",
                    methods=[
                        aiohttp.hdrs.METH_POST,
                        aiohttp.hdrs.METH_GET,  # Allows GraphiQL in development
                    ]
                    if SHARED_CONFIG.is_development
                    else [aiohttp.hdrs.METH_POST],
                    endpoint=internal_graphql_app,
                ),
            ],
        ),
    ],
    exception_handlers=exception_handlers,
    middleware=[
        # CORS is needed only for dashboard to API communications.
        Middleware(
            CORSMiddleware,
            allow_origins=[
                SHARED_CONFIG.eave_dashboard_base_url_public,
                SHARED_CONFIG.eave_admin_base_url_public,
            ],
            allow_methods=[
                aiohttp.hdrs.METH_GET,
                aiohttp.hdrs.METH_POST,
                aiohttp.hdrs.METH_HEAD,
                aiohttp.hdrs.METH_OPTIONS,
            ],
            allow_credentials=True,
        ),
    ],
    lifespan=_app_lifespan,
)
