import enum
from typing import Annotated
from uuid import uuid4

import strawberry

import eave.core.database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.resolvers.refresh_tokens import make_auth_token_pair
from eave.core.graphql.types.account import Account
from eave.core.graphql.types.auth_token_pair import AuthTokenPair
from eave.core.lib.analytics import ANALYTICS
from eave.core.orm.account import AccountOrm, test_password_strength_or_exception
from eave.stdlib.exceptions import InvalidJWSError
from eave.stdlib.jwt import JWTPurpose, create_jws, validate_jws_or_exception, validate_jws_pair_or_exception

@strawberry.input
class CreateAccountInput:
    email: str
    plaintext_password: str

@strawberry.enum
class CreateAccountErrorCode(enum.Enum):
    INVALID_EMAIL = enum.auto()
    WEAK_PASSWORD = enum.auto()
    ACCOUNT_EXISTS = enum.auto()


@strawberry.type
class CreateAccountSuccess:
    account: Account
    auth_tokens: AuthTokenPair


@strawberry.type
class CreateAccountError:
    error_code: CreateAccountErrorCode


CreateAccountResult = Annotated[CreateAccountSuccess | CreateAccountError, strawberry.union("CreateAccountResult")]

async def create_account_mutation(*, info: strawberry.Info[GraphQLContext], input: CreateAccountInput) -> CreateAccountResult:
    test_password_strength_or_exception(input.plaintext_password)

    async with eave.core.database.async_session.begin() as db_session:
        account_orm = await AccountOrm.build(
            session=db_session,
            email=input.email,
            plaintext_password=input.plaintext_password,
        ).save(db_session)

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
