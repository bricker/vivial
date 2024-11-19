import aiohttp.hdrs
import starlette.applications
import starlette.endpoints
import stripe
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route
from strawberry import Schema
from strawberry.asgi import GraphQL
from strawberry.schema.config import StrawberryConfig

import eave.core.endpoints
import eave.stdlib.time
from eave.core.config import CORE_API_APP_CONFIG
from eave.core.graphql.mutation import Mutation
from eave.core.graphql.query import Query
from eave.stdlib import cache
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER

from .database import async_engine

eave.stdlib.time.set_utc()

try:
    stripe.api_key = CORE_API_APP_CONFIG.stripe_secret_key
except Exception as e:
    LOGGER.exception(e)
    LOGGER.warning("Stripe API key not set! Stripe functionality will not work.")

schema = Schema(
    query=Query,
    mutation=Mutation,
    config=StrawberryConfig(
        auto_camel_case=True,
    ),
)

graphql_app = GraphQL(schema=schema)


async def graceful_shutdown() -> None:
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
            endpoint=eave.core.endpoints.StatusEndpoint,
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
            endpoint=eave.core.endpoints.HealthEndpoint,
            methods=[aiohttp.hdrs.METH_GET],
        ),
        Route(
            path="/favicon.ico",
            endpoint=eave.core.endpoints.NoopEndpoint,
            methods=[aiohttp.hdrs.METH_GET],
        ),
        Route(
            path="/graphql",
            methods=[
                aiohttp.hdrs.METH_POST,
            ],
            endpoint=graphql_app,
        ),
    ],
    middleware=[
        # CORS is needed only for dashboard to API communications.
        Middleware(
            CORSMiddleware,
            allow_origins=[
                SHARED_CONFIG.eave_dashboard_base_url_public,
            ],
            allow_methods=[
                aiohttp.hdrs.METH_GET,
                aiohttp.hdrs.METH_POST,
                aiohttp.hdrs.METH_PUT,
                aiohttp.hdrs.METH_PATCH,
                aiohttp.hdrs.METH_DELETE,
                aiohttp.hdrs.METH_HEAD,
                aiohttp.hdrs.METH_OPTIONS,
            ],
            allow_credentials=True,
        ),
    ],
    on_shutdown=[graceful_shutdown],
)
