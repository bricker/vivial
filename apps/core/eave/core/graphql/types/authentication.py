import enum
from typing import Annotated
import strawberry

from eave.core.graphql.types.account import Account

@strawberry.enum
class AuthenticationErrorCode(enum.StrEnum):
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"

@strawberry.type
class LoginSuccess:
    account: Account
    auth_tokens: AuthTokens

@strawberry.type
class LoginError:
    error_code: AuthenticationErrorCode


LoginResult = Annotated[
    LoginSuccess | LoginError, strawberry.union("LoginResult")
]

