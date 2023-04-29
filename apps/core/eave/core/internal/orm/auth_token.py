from . import UUID_DEFAULT_EXPR, Base, make_team_fk
from ... import EAVE_API_JWT_ISSUER, EAVE_API_SIGNING_KEY
from .account import AccountOrm


import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.exceptions as eave_exceptions
import eave.stdlib.core_api.operations as eave_ops
import eave.stdlib.jwt as eave_jwt
import eave.stdlib.util as eave_util
from sqlalchemy import ForeignKeyConstraint, Index, PrimaryKeyConstraint, Select, func, null, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from eave.stdlib import logger


from dataclasses import dataclass
from datetime import datetime
from typing import Dict, NotRequired, Optional, Required, Self, Tuple, TypedDict, Unpack
from uuid import UUID


class AuthTokenOrm(Base):
    __tablename__ = "auth_tokens"
    __table_args__ = (
        PrimaryKeyConstraint(
            "team_id",
            "account_id",
            "id",
        ),

        make_team_fk(),

        ForeignKeyConstraint(
            ["team_id", "account_id"],
            ["accounts.team_id", "accounts.id"],
        ),
        Index(
            "token_pair",
            "access_token_hashed",
            "refresh_token_hashed",
            unique=True,
        ),
        Index(
            "jwt_claims",
            "access_token_hashed",
            "aud",
            "iss",
            "expires",
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    account_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    access_token_hashed: Mapped[str] = mapped_column(index=True, unique=True)
    refresh_token_hashed: Mapped[str] = mapped_column(index=True, unique=True)
    jti: Mapped[str] = mapped_column()
    iss: Mapped[str] = mapped_column()
    aud: Mapped[str] = mapped_column()
    expires: Mapped[datetime] = mapped_column()
    invalidated: Mapped[Optional[datetime]] = mapped_column(server_default=None)
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(cls, session: AsyncSession, team_id: UUID, account_id: UUID, access_token: str, refresh_token: str, jti: str, iss: str, aud: str, expires: datetime, invalidated: Optional[datetime] = None) -> Self:
        obj = cls(
            team_id=team_id,
            account_id=account_id,
            access_token_hashed=eave_util.sha256hexdigest(access_token),
            refresh_token_hashed=eave_util.sha256hexdigest(refresh_token),
            jti=jti,
            iss=iss,
            aud=aud,
            expires=expires,
            invalidated=invalidated,
        )

        session.add(obj)
        return obj

    class _selectparams(TypedDict):
        access_token: Required[str]
        aud: Required[str]
        refresh_token: NotRequired[str]
        allow_expired: NotRequired[bool]

    @classmethod
    def _build_select(cls, **kwargs: Unpack[_selectparams]) -> Select[Tuple[Self]]:
        access_token_hashed = eave_util.sha256hexdigest(kwargs["access_token"])

        lookup = (
            select(cls)
            .where(cls.access_token_hashed == access_token_hashed)
            .where(cls.invalidated == null())
            .where(cls.iss == EAVE_API_JWT_ISSUER)
            .where(cls.aud == kwargs["aud"])
            .limit(1)
        )

        if refresh_token := kwargs.get("refresh_token"):
            refresh_token_hashed = eave_util.sha256hexdigest(refresh_token)
            lookup = lookup.where(cls.refresh_token_hashed == refresh_token_hashed)

        if kwargs.get("allow_expired") is not True:
            lookup = lookup.where(cls.expires > func.current_timestamp())

        assert lookup.whereclause is not None
        return lookup

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, log_context: Optional[Dict[str,str]] = None, **kwargs: Unpack[_selectparams]) -> Self:
        lookup = cls._build_select(**kwargs)
        result = (await session.scalars(lookup)).one()
        if result.expired and kwargs.get("allow_expired") is not True:
            logger.error("Access token found, but it is expired, and expired tokens are omitted from the query.", extra=log_context)
            raise eave_exceptions.AccessTokenExpiredError()

        return result

    @dataclass(frozen=True)
    class AuthTokenBundle:
        auth_token: "AuthTokenOrm"
        account: AccountOrm

    @classmethod
    async def find_and_verify_or_exception(
        cls,
        session: AsyncSession,
        log_context: Optional[Dict[str,str]] = None,
        **kwargs: Unpack[_selectparams],
    ) -> AuthTokenBundle:
        """
        Finds the AuthTokenOrm and associated AccountOrm, validates the passed-in access token,
        then returns the AuthTokenOrm and AccountOrm.
        """
        access_token = kwargs["access_token"]
        allow_expired = kwargs.get("allow_expired", False)

        if refresh_token := kwargs.get("refresh_token"):
            # Short-circuit if the access token and refresh token weren't issued together.
            eave_jwt.validate_jwt_pair_or_exception(
                jwt_encoded_a=access_token, jwt_encoded_b=refresh_token, signing_key=EAVE_API_SIGNING_KEY
            )

        auth_token_orm = await cls.one_or_exception(
            session=session,
            log_context=log_context,
            **kwargs,
        )

        if (auth_token_orm.expired and allow_expired is not True) or (auth_token_orm.invalidated is not None):
            logger.error("auth token expired or invalidated", extra=log_context)
            raise eave_exceptions.AccessTokenExpiredError()

        account = await AccountOrm.one_or_exception(
            session=session,
            id=auth_token_orm.account_id,
            team_id=auth_token_orm.team_id,
        )

        eave_jwt.validate_jwt_or_exception(
            jwt_encoded=access_token,
            signing_key=EAVE_API_SIGNING_KEY,
            expected_issuer=EAVE_API_JWT_ISSUER,
            expected_audience=auth_token_orm.aud,
            expected_subject=str(account.id),
            expected_jti=auth_token_orm.jti,
            expected_expiry=auth_token_orm.expires,
            allow_expired=allow_expired,
        )

        return AuthTokenOrm.AuthTokenBundle(auth_token=auth_token_orm, account=account)

    @dataclass(frozen=True)
    class JWTBundle:
        access_token: eave_jwt.JWT
        refresh_token: eave_jwt.JWT
        auth_token: "AuthTokenOrm"
        account: AccountOrm

    @classmethod
    async def create_token_pair_for_account(
        cls,
        session: AsyncSession,
        account: AccountOrm,
        audience: eave_origins.EaveOrigin,
        log_context: Optional[Dict[str,str]] = None,
    ) -> JWTBundle:
        """
        Creates an Access Token/Refresh Token pair for the given account and audience,
        and adds the resulting AuthTokenOrm object to the db session.
        """
        sub = str(account.id)
        aud = audience.value

        new_access_token_jwt = eave_jwt.create_jwt(
            signing_key=EAVE_API_SIGNING_KEY,
            purpose=eave_jwt.JWTPurpose.access,
            iss=EAVE_API_JWT_ISSUER,
            aud=aud,
            sub=sub,
        )

        new_refresh_token_jwt = eave_jwt.create_jwt(
            signing_key=EAVE_API_SIGNING_KEY,
            purpose=eave_jwt.JWTPurpose.refresh,
            iss=EAVE_API_JWT_ISSUER,
            aud=aud,
            sub=sub,
            jti=new_access_token_jwt.payload.jti,
            exp_minutes=(
                60 * 24 * 30
            ),  # 30 days. If the user goes 30 days without logging in, they will have to login again.
        )

        new_auth_token_orm = await cls.create(
            session=session,
            account_id=account.id,
            team_id=account.team_id,
            iss=EAVE_API_JWT_ISSUER,
            aud=aud,
            jti=new_access_token_jwt.payload.jti,
            access_token=str(new_access_token_jwt),
            refresh_token=str(new_refresh_token_jwt),
            expires=datetime.utcfromtimestamp(float(new_access_token_jwt.payload.exp)),
        )

        return AuthTokenOrm.JWTBundle(
            access_token=new_access_token_jwt,
            refresh_token=new_refresh_token_jwt,
            auth_token=new_auth_token_orm,
            account=account,
        )

    @property
    def expired(self) -> bool:
        return datetime.utcnow() >= self.expires