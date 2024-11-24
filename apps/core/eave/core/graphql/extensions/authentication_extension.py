from collections.abc import Awaitable, Callable
import enum
from http import HTTPStatus
from typing import Any, Literal
from uuid import UUID

import strawberry
from strawberry.extensions import FieldExtension
from strawberry.http.exceptions import HTTPException
from starlette.responses import JSONResponse

from eave.core.auth_cookies import delete_auth_cookies
from eave.core.config import JWT_AUDIENCE, JWT_ISSUER
from eave.core.graphql.context import GraphQLContext
from eave.stdlib.cookies import EAVE_ACCESS_TOKEN_COOKIE_NAME
from eave.stdlib.http_exceptions import UnauthorizedError
from eave.stdlib.jwt import JWTPurpose, validate_jws_or_exception, AccessTokenExpiredError, InvalidJWSError, InvalidJWTError, InvalidTokenError
from eave.stdlib.logging import LOGGER
from eave.stdlib.cookies import delete_http_cookie

@strawberry.enum
class ViewerAuthenticationAction(enum.Enum):
    REFRESH_ACCESS_TOKEN = enum.auto()
    FORCE_LOGOUT = enum.auto()

@strawberry.type
class UnauthenticatedViewer:
    reason: ViewerAuthenticationAction

class AuthenticationExtension(FieldExtension):
    def __init__(self, *, allow_anonymous: bool = False) -> None:
        self.allow_anonymous = allow_anonymous

    async def resolve_async(
        self, next_: Callable[..., Awaitable[Any]], source: Any, info: strawberry.Info[GraphQLContext], **kwargs
    ) -> Any:
        encoded_jws = info.context["request"].cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME)
        try:
            if encoded_jws:
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
            else:
                if not self.allow_anonymous:
                    raise InvalidTokenError("missing access token")

        except AccessTokenExpiredError:
            return UnauthenticatedViewer(reason=ViewerAuthenticationAction.REFRESH_ACCESS_TOKEN)

        except InvalidTokenError:
            delete_auth_cookies(response=info.context["response"])
            return UnauthenticatedViewer(reason=ViewerAuthenticationAction.FORCE_LOGOUT)
