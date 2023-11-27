import http
import starlette.applications
from starlette.routing import Route
import strawberry
from strawberry.schema.config import StrawberryConfig
from eave.core.graphql.mutation import Mutation

from eave.core.graphql.query import Query
from strawberry.asgi import GraphQL

schema = strawberry.federation.Schema(
    query=Query,
    mutation=Mutation,
    enable_federation_2=True,
    config=StrawberryConfig(
        auto_camel_case=True,
    )
)

graphql_app = GraphQL(schema)

app = starlette.applications.Starlette(
    routes=[
        Route(
            path="/graphql",
            methods=[http.HTTPMethod.POST, http.HTTPMethod.GET],
            endpoint=graphql_app,
        ),
    ],
)
