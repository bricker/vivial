from collections.abc import Iterator
from typing import cast, override

from strawberry.extensions import SchemaExtension

from eave.core.graphql.context import GraphQLContext
from eave.stdlib.analytics import SEGMENT_ANONYMOUS_ID_COOKIE_NAME
from eave.stdlib.logging import LOGGER


class VisitorIdExtension(SchemaExtension):
    @override
    def on_operation(self) -> Iterator[None]:
        try:
            ctx = cast(GraphQLContext, self.execution_context.context)
            # Safety because `context` is typed as `Any`
            visitor_id = ctx["request"].cookies.get(SEGMENT_ANONYMOUS_ID_COOKIE_NAME)
            ctx["visitor_id"] = visitor_id
        except Exception as e:
            LOGGER.exception(e)

        yield
