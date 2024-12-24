from collections.abc import Awaitable, Callable
from typing import Any, override

from graphql import GraphQLResolveInfo
from strawberry.extensions import SchemaExtension

from eave.stdlib.analytics import SEGMENT_ANONYMOUS_ID_COOKIE_NAME


class VisitorIdExtension(SchemaExtension):
    @override
    def resolve(
        self, next_: Callable[..., Awaitable[Any]], root: Any, info: GraphQLResolveInfo, *args, **kwargs
    ) -> Any:
        visitor_id = info.context["request"].cookies.get(SEGMENT_ANONYMOUS_ID_COOKIE_NAME)
        info.context["visitor_id"] = visitor_id

        return next_(root, info, *args, **kwargs)
