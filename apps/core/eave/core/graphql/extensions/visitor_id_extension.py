from collections.abc import Awaitable, Callable, Iterator
from typing import Any, override

from graphql import GraphQLResolveInfo
from strawberry.extensions import SchemaExtension

from eave.stdlib.analytics import SEGMENT_ANONYMOUS_ID_COOKIE_NAME
from eave.stdlib.logging import LOGGER


class VisitorIdExtension(SchemaExtension):
    @override
    def on_operation(self) -> Iterator[None]:
        LOGGER.debug("VisitorIdExtension")

        try:
            # Safety because `context` is typed as `Any`
            visitor_id = self.execution_context.context["request"].cookies.get(SEGMENT_ANONYMOUS_ID_COOKIE_NAME)
            self.execution_context.context["visitor_id"] = visitor_id
        except Exception as e:
            LOGGER.exception(e)

        yield
