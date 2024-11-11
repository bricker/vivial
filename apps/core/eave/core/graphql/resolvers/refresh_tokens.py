import enum
from typing import Annotated
from uuid import UUID, uuid4

import strawberry

from eave.core.config import JWT_AUDIENCE, JWT_ISSUER
import eave.core.database
from eave.core.graphql.context import GraphQLContext
from eave.core.graphql.types.account import Account
from eave.core.graphql.types.auth_token_pair import AuthTokenPair
from eave.core.lib.analytics import ANALYTICS
from eave.core.orm.account import AccountOrm, test_password_strength_or_exception
from eave.stdlib.exceptions import InvalidJWSError
from eave.stdlib.jwt import JWTPurpose, create_jws, validate_jws_or_exception, validate_jws_pair_or_exception


@strawberry.input
class RefreshTokensInput:
    access_token: str
    refresh_token: str

@strawberry.enum
class RefreshTokensErrorCode(enum.Enum):
    INVALID_TOKENS = enum.auto()


@strawberry.type
class RefreshTokensSuccess:
    auth_tokens: AuthTokenPair


@strawberry.type
class RefreshTokensError:
    error_code: RefreshTokensErrorCode


RefreshTokensResult = Annotated[RefreshTokensSuccess | RefreshTokensError, strawberry.union("RefreshTokensResult")]

async def refresh_tokens_mutation(*, info: strawberry.Info[GraphQLContext], input: RefreshTokensInput) -> RefreshTokensResult:
    access_jws = validate_jws_or_exception(
        encoded_jws=input.access_token,
        expected_issuer=JWT_ISSUER,
        expected_audience=JWT_AUDIENCE,
        expected_purpose=JWTPurpose.ACCESS,
    )
    refresh_jws = validate_jws_or_exception(
        encoded_jws=input.refresh_token,
        expected_issuer=JWT_ISSUER,
        expected_audience=JWT_AUDIENCE,
        expected_purpose=JWTPurpose.REFRESH,
    )

    if validate_jws_pair_or_exception(access_token=access_jws, refresh_token=refresh_jws):
        new_auth_token_pair = make_auth_token_pair(account_id=UUID(refresh_jws.payload.sub))
        return RefreshTokensSuccess(auth_tokens=new_auth_token_pair)
    else:
        return RefreshTokensError(error_code=RefreshTokensErrorCode.INVALID_TOKENS)


def make_auth_token_pair(*, account_id: UUID) -> AuthTokenPair:
    jwt_id = str(uuid4())

    access_token = create_jws(
        purpose=JWTPurpose.ACCESS,
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE,
        subject=str(account_id),
        jwt_id=jwt_id,
        max_age_minutes=10,
    )

    refresh_token = create_jws(
        purpose=JWTPurpose.REFRESH,
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE,
        subject=str(account_id),
        jwt_id=jwt_id,
        max_age_minutes=60 * 24 * 365,
    )

    return AuthTokenPair(access_token=access_token, refresh_token=refresh_token)
