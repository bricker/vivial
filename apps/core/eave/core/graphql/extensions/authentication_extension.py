from collections.abc import Awaitable, Callable
from typing import Any

import strawberry
from strawberry.extensions import FieldExtension

from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.authentication import JWT_AUDIENCE, JWT_ISSUER
from eave.stdlib.cookies import EAVE_ACCESS_TOKEN_COOKIE_NAME
from eave.stdlib.jwt import JWTPurpose, validate_jws_or_exception


class AuthenticationExtension(FieldExtension):
    async def resolve_async(
        self, next_: Callable[..., Awaitable[Any]], source: Any, info: strawberry.Info[GraphQLContext], **kwargs
    ) -> Any:
        jws = info.context.request.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME)
        if not jws:
            raise Exception("missing access token")

        validate_jws_or_exception(
            encoded_jws=jws,
            expected_audience=JWT_AUDIENCE,
            expected_issuer=JWT_ISSUER,
            expected_purpose=JWTPurpose.ACCESS,
        )

        result = await next_(source, info, **kwargs)
        return result
