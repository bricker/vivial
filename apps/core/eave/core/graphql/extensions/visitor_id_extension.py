from collections.abc import Iterator
from typing import cast, override

from strawberry.extensions import SchemaExtension

from eave.core.graphql.context import GraphQLContext, log_ctx
from eave.stdlib.analytics import SEGMENT_ANONYMOUS_ID_COOKIE_NAME
from eave.stdlib.logging import LOGGER


class VisitorIdExtension(SchemaExtension):
    @override
    def on_operation(self) -> Iterator[None]:
        ctx = cast(GraphQLContext, self.execution_context.context)

        try:
            # Safety because `context` is typed as `Any`
            visitor_id = ctx["request"].cookies.get(SEGMENT_ANONYMOUS_ID_COOKIE_NAME)
            ctx["visitor_id"] = visitor_id
        except Exception as e:
            LOGGER.exception(e, log_ctx(ctx))

        yield
