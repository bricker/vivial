from collections.abc import Awaitable, Callable
from typing import Any
from uuid import UUID, uuid4

import strawberry
from strawberry.extensions import FieldExtension

from eave.core.config import JWT_AUDIENCE, JWT_ISSUER
from eave.core.graphql.context import GraphQLContext
from eave.stdlib.cookies import EAVE_ACCESS_TOKEN_COOKIE_NAME
from eave.stdlib.exceptions import UnauthorizedError
from eave.stdlib.jwt import JWTPurpose, validate_jws_or_exception


class AuthenticationExtension(FieldExtension):
    def __init__(self, *, allow_anonymous: bool = False) -> None:
        self.allow_anonymous = allow_anonymous

    async def resolve_async(
        self, next_: Callable[..., Awaitable[Any]], source: Any, info: strawberry.Info[GraphQLContext], **kwargs
    ) -> Any:
        encoded_jws = info.context["request"].cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME)
        if encoded_jws:
            jws = validate_jws_or_exception(
                encoded_jws=encoded_jws,
                expected_audience=JWT_AUDIENCE,
                expected_issuer=JWT_ISSUER,
                expected_purpose=JWTPurpose.ACCESS,
            )

            info.context["authenticated_account_id"] = UUID(jws.payload.sub)
        else:
            if not self.allow_anonymous:
                raise UnauthorizedError()

        result = await next_(source, info, **kwargs)
        return result
