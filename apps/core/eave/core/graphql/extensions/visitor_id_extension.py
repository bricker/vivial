from collections.abc import Iterator
from typing import cast, override

from strawberry.extensions import SchemaExtension

from eave.core.graphql.context import GraphQLContext, log_ctx
from eave.stdlib.analytics import SEGMENT_ANONYMOUS_ID_COOKIE_NAME
from eave.stdlib.exceptions import suppress_in_production
from eave.stdlib.logging import LOGGER


class VisitorIdExtension(SchemaExtension):
    @override
    def on_operation(self) -> Iterator[None]:
        gql_ctx = cast(GraphQLContext, self.execution_context.context)

        with suppress_in_production(Exception, ctx=log_ctx(gql_ctx)):
            # Safety because `context` is typed as `Any`
            visitor_id = gql_ctx["request"].cookies.get(SEGMENT_ANONYMOUS_ID_COOKIE_NAME)
            gql_ctx["visitor_id"] = visitor_id

        yield
