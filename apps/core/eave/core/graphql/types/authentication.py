import enum
from typing import Annotated

import strawberry

from .account import Account


@strawberry.type
class AuthTokenPair:
    access_token: str
    refresh_token: str


@strawberry.enum
class AuthenticationErrorCode(enum.StrEnum):
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    INVALID_EMAIL = "INVALID_EMAIL"


@strawberry.type
class LoginSuccess:
    account: Account
    auth_tokens: AuthTokenPair


@strawberry.type
class LoginError:
    error_code: AuthenticationErrorCode


LoginResult = Annotated[LoginSuccess | LoginError, strawberry.union("LoginResult")]
