import enum
from typing import Annotated

import strawberry

import eave.core.database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.refresh_tokens import make_auth_token_pair
from eave.core.graphql.types.account import Account
from eave.core.graphql.types.auth_token_pair import AuthTokenPair
from eave.core.lib.analytics import ANALYTICS
from eave.core.orm.account import AccountOrm
from eave.stdlib.exceptions import ValidationError


@strawberry.input
class CreateAccountInput:
    email: str
    plaintext_password: str


@strawberry.enum
class CreateAccountErrorCode(enum.Enum):
    VALIDATION_ERROR = enum.auto()
    ACCOUNT_EXISTS = enum.auto()


@strawberry.type
class CreateAccountSuccess:
    account: Account
    auth_tokens: AuthTokenPair


@strawberry.type
class CreateAccountError:
    error_code: CreateAccountErrorCode


CreateAccountResult = Annotated[CreateAccountSuccess | CreateAccountError, strawberry.union("CreateAccountResult")]


async def create_account_mutation(
    *, info: strawberry.Info[GraphQLContext], input: CreateAccountInput
) -> CreateAccountResult:
    async with eave.core.database.async_session.begin() as db_session:
        existing_account_orm = await db_session.scalar(AccountOrm.select(email=input.email).limit(1))
        if existing_account_orm:
            return CreateAccountError(error_code=CreateAccountErrorCode.ACCOUNT_EXISTS)

        try:
            account_orm = AccountOrm.build(
                email=input.email,
                plaintext_password=input.plaintext_password,
            )
        except ValidationError:
            return CreateAccountError(error_code=CreateAccountErrorCode.VALIDATION_ERROR)

        await account_orm.save(db_session)

    ANALYTICS.identify(
        account_id=account_orm.id,
        # TODO: visitor_id
        extra_properties={
            "email": account_orm.email,
        },
    )

    ANALYTICS.track(
        event_name="signup",
        account_id=account_orm.id,
    )

    auth_token_pair = make_auth_token_pair(account_id=account_orm.id)

    account = Account.from_orm(account_orm)
    return CreateAccountSuccess(account=account, auth_tokens=auth_token_pair)
