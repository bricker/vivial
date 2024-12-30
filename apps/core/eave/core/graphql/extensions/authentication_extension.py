import enum
from collections.abc import Awaitable, Callable
from typing import Any, override
from uuid import UUID

import strawberry
from strawberry.extensions import FieldExtension

from eave.core.auth_cookies import ACCESS_TOKEN_COOKIE_NAME, delete_auth_cookies
from eave.core.config import JWT_AUDIENCE, JWT_ISSUER
from eave.core.graphql.context import GraphQLContext
from eave.stdlib.jwt import (
    AccessTokenExpiredError,
    InvalidTokenError,
    JWTPurpose,
    validate_jws_or_exception,
)
from eave.stdlib.logging import LOGGER


@strawberry.enum
class ViewerAuthenticationAction(enum.Enum):
    REFRESH_ACCESS_TOKEN = enum.auto()
    FORCE_LOGOUT = enum.auto()


@strawberry.enum
class AuthenticationFailureReason(enum.Enum):
    ACCESS_TOKEN_EXPIRED = enum.auto()
    ACCESS_TOKEN_INVALID = enum.auto()


@strawberry.type
class UnauthenticatedViewer:
    auth_action: ViewerAuthenticationAction = strawberry.field(deprecation_reason="Use authFailureReason")
    auth_failure_reason: AuthenticationFailureReason


class AuthenticationExtension(FieldExtension):
    @override
    async def resolve_async(
        self, next_: Callable[..., Awaitable[Any]], source: Any, info: strawberry.Info[GraphQLContext], **kwargs
    ) -> Any:
        LOGGER.debug("AuthenticationExtension")

        encoded_jws = info.context["request"].cookies.get(ACCESS_TOKEN_COOKIE_NAME)
        try:
            if not encoded_jws:
                raise InvalidTokenError("missing access token")

            jws = validate_jws_or_exception(
                encoded_jws=encoded_jws,
                expected_audience=JWT_AUDIENCE,
                expected_issuer=JWT_ISSUER,
                expected_purpose=JWTPurpose.ACCESS,
                expired_ok=False,
            )

            info.context["authenticated_account_id"] = UUID(jws.payload.sub)

            result = await next_(source, info, **kwargs)
            return result
        except AccessTokenExpiredError:
            return UnauthenticatedViewer(
                auth_action=ViewerAuthenticationAction.REFRESH_ACCESS_TOKEN,
                auth_failure_reason=AuthenticationFailureReason.ACCESS_TOKEN_EXPIRED,
            )

        except InvalidTokenError:
            delete_auth_cookies(response=info.context["response"])
            return UnauthenticatedViewer(
                auth_failure_reason=AuthenticationFailureReason.ACCESS_TOKEN_INVALID,
                auth_action=ViewerAuthenticationAction.FORCE_LOGOUT,
            )
