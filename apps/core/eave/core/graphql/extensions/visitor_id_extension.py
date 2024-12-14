from collections.abc import Awaitable, Callable
from typing import Any

import strawberry
from strawberry.extensions import FieldExtension

from eave.core.graphql.context import GraphQLContext
from eave.stdlib.analytics import SEGMENT_ANONYMOUS_ID_COOKIE_NAME


class VisitorIdExtension(FieldExtension):
    async def resolve_async(
        self, next_: Callable[..., Awaitable[Any]], source: Any, info: strawberry.Info[GraphQLContext], **kwargs
    ) -> Any:
        visitor_id = info.context["request"].cookies.get(SEGMENT_ANONYMOUS_ID_COOKIE_NAME)
        info.context["visitor_id"] = visitor_id
