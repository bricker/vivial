from typing import Any, Awaitable, Callable

from eave.stdlib.cookies import EAVE_ACCESS_TOKEN_COOKIE_NAME
import strawberry
from strawberry.extensions import FieldExtension

from eave.core.graphql.context import GraphQLContext

class AuthenticationExtension(FieldExtension):
    async def resolve_async(
        self,
        next_: Callable[..., Awaitable[Any]],
        source: Any,
        info: strawberry.Info[GraphQLContext],
        **kwargs
    ) -> Any:
        encrypted_jwt = info.context.request.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME)
        if not encrypted_jwt:
            raise Exception("missing access token")

        validated_jwt = jwt.validate_jwt_or_exception(jwt=encrypted_jwt)

        result = await next_(source, info, **kwargs)
        return result
