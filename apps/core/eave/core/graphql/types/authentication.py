import enum
from typing import Annotated
from uuid import UUID
import strawberry

from eave.core.graphql.types.user_profile import UserProfile

@strawberry.type
class Account:
    id: UUID = strawberry.field()
    email: str = strawberry.field()
    user_profile: UserProfile

@strawberry.type
class AuthTokenPair:
    access_token: str
    refresh_token: str

@strawberry.enum
class AuthenticationErrorCode(enum.StrEnum):
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"

@strawberry.type
class LoginSuccess:
    account: Account
    auth_tokens: AuthTokenPair

@strawberry.type
class LoginError:
    error_code: AuthenticationErrorCode


LoginResult = Annotated[
    LoginSuccess | LoginError, strawberry.union("LoginResult")
]

