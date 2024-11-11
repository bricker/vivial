import enum
from typing import Annotated
from uuid import uuid4

import strawberry

from eave.core.config import JWT_AUDIENCE, JWT_ISSUER
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
class LoginInput:
    email: str
    plaintext_password: str

@strawberry.enum
class AuthenticationErrorCode(enum.Enum):
    INVALID_CREDENTIALS = enum.auto()
    INVALID_EMAIL = enum.auto()


@strawberry.type
class LoginSuccess:
    account: Account
    auth_tokens: AuthTokenPair


@strawberry.type
class LoginError:
    error_code: AuthenticationErrorCode

LoginResult = Annotated[LoginSuccess | LoginError, strawberry.union("LoginResult")]


async def login_mutation(*, info: strawberry.Info[GraphQLContext], input: LoginInput) -> LoginResult:
    async with eave.core.database.async_session.begin() as db_session:
        account_orm = await AccountOrm.one_or_exception(
            session=db_session,
            params=AccountOrm.QueryParams(
                email=input.email,
            ),
        )

        if account_orm.validate_password_or_exception(input.plaintext_password):
            auth_token_pair = make_auth_token_pair(account_id=account_orm.id)
            account = Account(
                id=account_orm.id,
                email=account_orm.email,
            )
            return LoginSuccess(account=account, auth_tokens=auth_token_pair)
        else:
            # TODO: Currently this won't be reached because credential failure will throw its own error.
            return LoginError(error_code=AuthenticationErrorCode.INVALID_CREDENTIALS)
