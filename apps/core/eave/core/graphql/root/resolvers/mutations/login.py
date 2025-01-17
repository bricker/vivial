import enum
from datetime import UTC, datetime
from typing import Annotated

import strawberry

import eave.core.database
from eave.core.auth_cookies import set_new_auth_cookies
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.account import Account
from eave.core.orm.account import AccountOrm, InvalidPasswordError


@strawberry.input
class LoginInput:
    email: str
    plaintext_password: str


@strawberry.type
class LoginSuccess:
    account: Account


@strawberry.enum
class LoginFailureReason(enum.Enum):
    INVALID_CREDENTIALS = enum.auto()


@strawberry.type
class LoginFailure:
    failure_reason: LoginFailureReason


LoginResult = Annotated[LoginSuccess | LoginFailure, strawberry.union("LoginResult")]


async def login_mutation(*, info: strawberry.Info[GraphQLContext], input: LoginInput) -> LoginResult:
    async with eave.core.database.async_session.begin() as db_session:
        account_orm = await db_session.scalar(AccountOrm.select(email=input.email).limit(1))
        if not account_orm:
            return LoginFailure(failure_reason=LoginFailureReason.INVALID_CREDENTIALS)

        try:
            account_orm.verify_password_or_exception(plaintext_password=input.plaintext_password)

            set_new_auth_cookies(response=info.context["response"], account_id=account_orm.id)
            account_orm.last_login = datetime.now(UTC)

        except InvalidPasswordError:
            return LoginFailure(failure_reason=LoginFailureReason.INVALID_CREDENTIALS)

        account = Account.from_orm(account_orm)
        return LoginSuccess(account=account)
