import enum
from typing import Annotated

import strawberry

import eave.core.database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.refresh_tokens import make_auth_token_pair
from eave.core.graphql.types.account import Account
from eave.core.graphql.types.auth_token_pair import AuthTokenPair
from eave.core.orm.account import AccountOrm


@strawberry.input
class LoginInput:
    email: str
    plaintext_password: str


@strawberry.enum
class LoginErrorCode(enum.Enum):
    INVALID_CREDENTIALS = enum.auto()
    UNKNOWN_ERROR = enum.auto()


@strawberry.type
class LoginSuccess:
    account: Account
    auth_tokens: AuthTokenPair


@strawberry.type
class LoginError:
    error_code: LoginErrorCode


LoginResult = Annotated[LoginSuccess | LoginError, strawberry.union("LoginResult")]


async def login_mutation(*, info: strawberry.Info[GraphQLContext], input: LoginInput) -> LoginResult:
    async with eave.core.database.async_session.begin() as db_session:
        account_orm = await db_session.scalar(AccountOrm.select(email=input.email).limit(1))
        if not account_orm:
            return LoginError(error_code=LoginErrorCode.INVALID_CREDENTIALS)

        if account_orm.verify_password_or_exception(input.plaintext_password):
            auth_token_pair = make_auth_token_pair(account_id=account_orm.id)
            account = Account(
                id=account_orm.id,
                email=account_orm.email,
            )
            return LoginSuccess(account=account, auth_tokens=auth_token_pair)
        else:
            return LoginError(error_code=LoginErrorCode.INVALID_CREDENTIALS)
