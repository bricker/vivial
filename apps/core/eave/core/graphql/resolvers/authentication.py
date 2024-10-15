from uuid import UUID, uuid4
from eave.stdlib.exceptions import InvalidJWSError
from eave.stdlib.jwt import create_jws, JWTPurpose, validate_jws_or_exception, validate_jws_pair_or_exception
import strawberry
from eave.core.graphql.types.authentication import Account
from eave.core.graphql.types.user_profile import UserProfile
import eave.core.internal.database
from starlette.requests import Request
from starlette.responses import Response

from eave.core.internal.orm.account import AccountOrm, test_password_strength_or_exception
from ..types.authentication import AuthTokenPair, LoginError, LoginResult, LoginSuccess, AuthenticationErrorCode

JWT_ISSUER = "core-api"
JWT_AUDIENCE = "core-api"

async def register_mutation(*, info: strawberry.Info, email: str, plaintext_password: str) -> None:
    test_password_strength_or_exception(plaintext_password)

async def login_mutation(*, info: strawberry.Info, email: str, plaintext_password: str) -> LoginResult:
    async with eave.core.internal.database.async_session.begin() as db_session:
        account = await AccountOrm.one_or_exception(
            session=db_session,
            params=AccountOrm.QueryParams(
                email=email,
            ),
        )

        if account.validate_password_or_exception(plaintext_password):
            auth_token_pair = _make_auth_token_pair(account_id=str(account.id))
            account = Account(
                id=account.id,
                email=account.email,
                user_profile=UserProfile(),
            )
            return LoginSuccess(account=account, auth_tokens=auth_token_pair)
        else:
            # TODO: Currently this won't be reached because credential failure will throw its own error.
            return LoginError(error_code=AuthenticationErrorCode.INVALID_CREDENTIALS)

async def refresh_tokens_mutation(*, info: strawberry.Info, access_token: str, refresh_token: str) -> AuthTokenPair:
    access_jws = validate_jws_or_exception(
        encoded_jws=access_token,
        expected_issuer=JWT_ISSUER,
        expected_audience=JWT_AUDIENCE,
        expected_purpose=JWTPurpose.ACCESS,
    )
    refresh_jws = validate_jws_or_exception(
        encoded_jws=refresh_token,
        expected_issuer=JWT_ISSUER,
        expected_audience=JWT_AUDIENCE,
        expected_purpose=JWTPurpose.REFRESH,
    )

    if validate_jws_pair_or_exception(access_token=access_jws, refresh_token=refresh_jws):
        new_auth_token_pair = _make_auth_token_pair(account_id=refresh_jws.payload.sub)
        return new_auth_token_pair
    else:
        # TODO: Currently this won't be reached.
        raise InvalidJWSError("mismatched tokens")

async def logout_mutation() -> None:
    pass

def _make_auth_token_pair(*, account_id: str) -> AuthTokenPair:
    jwt_id = str(uuid4())

    access_token = create_jws(
        purpose=JWTPurpose.ACCESS,
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE,
        subject=account_id,
        jwt_id=jwt_id,
        max_age_minutes=10,
    )

    refresh_token = create_jws(
        purpose=JWTPurpose.REFRESH,
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE,
        subject=account_id,
        jwt_id=jwt_id,
        max_age_minutes=60*24*365,
    )

    return AuthTokenPair(access_token=access_token, refresh_token=refresh_token)
