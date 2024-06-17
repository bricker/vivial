import typing
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Self
from uuid import UUID

from sqlalchemy import Index, Select, func, or_, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

import eave.core.internal
import eave.stdlib.exceptions
from eave.stdlib.core_api.models.account import AuthenticatedAccount, AuthProvider
from eave.stdlib.exceptions import MissingOAuthCredentialsError
from eave.stdlib.logging import LogContext

from .base import Base
from .team import TeamOrm
from .util import UUID_DEFAULT_EXPR, make_team_composite_pk, make_team_fk


class AccountOrm(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        make_team_composite_pk(table_name="accounts"),
        make_team_fk(),
        Index(
            "auth_provider_auth_id",
            "auth_provider",
            "auth_id",
            unique=True,
        ),
        Index(
            None,
            "auth_provider",
            "auth_id",
            "access_token",
            unique=True,
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)

    visitor_id: Mapped[UUID | None] = mapped_column()
    """DEPRECATED"""

    opaque_utm_params: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    """DEPRECATED"""

    auth_provider: Mapped[AuthProvider] = mapped_column()
    """3rd party login provider"""
    auth_id: Mapped[str] = mapped_column()
    """userid from 3rd party auth_provider"""
    access_token: Mapped[str] = mapped_column()
    """access token from 3rd party"""
    refresh_token: Mapped[str | None] = mapped_column(server_default=None)
    previous_access_token: Mapped[str | None] = mapped_column(server_default=None)
    """When a new access token is acquired, move the previous value here. It can be used for lookup to mitigate race conditions between client and server"""
    email: Mapped[str | None] = mapped_column(server_default=None)
    """refresh token from 3rd party"""
    last_login: Mapped[datetime | None] = mapped_column(server_default=func.current_timestamp(), nullable=True)
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: UUID,
        auth_provider: AuthProvider,
        auth_id: str,
        access_token: str,
        refresh_token: str | None,
        email: str | None = None,
    ) -> Self:
        obj = cls(
            team_id=team_id,
            auth_provider=auth_provider,
            auth_id=auth_id,
            access_token=access_token,
            refresh_token=refresh_token,
            email=email,
        )

        session.add(obj)
        await session.flush()
        return obj

    @dataclass
    class QueryParams:
        id: uuid.UUID | None = None
        team_id: uuid.UUID | None = None
        auth_provider: AuthProvider | None = None
        auth_id: str | None = None
        access_token: str | None = None

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[tuple[Self]]:
        lookup = select(cls).limit(1)

        if params.id is not None:
            lookup = lookup.where(cls.id == params.id)

        if params.team_id is not None:
            lookup = lookup.where(cls.team_id == params.team_id)

        if params.auth_provider is not None:
            lookup = lookup.where(cls.auth_provider == params.auth_provider)

        if params.auth_id is not None:
            lookup = lookup.where(cls.auth_id == params.auth_id)

        if params.access_token is not None:
            lookup = lookup.where(
                or_(
                    cls.access_token == params.access_token,
                    cls.previous_access_token == params.access_token,
                )
            )

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup

    @classmethod
    async def query(cls, session: AsyncSession, params: QueryParams) -> Self:
        lookup = cls._build_query(params=params)
        result = (await session.scalars(lookup)).one()
        return result

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, params: QueryParams) -> Self:
        lookup = cls._build_query(params=params)
        result = (await session.scalars(lookup)).one()
        return result

    @classmethod
    async def one_or_none(cls, session: AsyncSession, params: QueryParams) -> Self | None:
        lookup = cls._build_query(params=params)
        result = await session.scalar(lookup)
        return result

    def set_tokens(self, session: AsyncSession, access_token: str | None, refresh_token: str | None) -> None:
        """
        The session parameter is unused but encourages the caller to use this function in an open DB session, so that the changes are applied when it's closed.
        """
        if access_token and access_token != self.access_token:
            self.previous_access_token = self.access_token
            self.access_token = access_token

        if refresh_token and refresh_token != self.refresh_token:
            self.refresh_token = refresh_token

    async def verify_oauth_or_exception(
        self, session: AsyncSession, ctx: LogContext | None = None
    ) -> typing.Literal[True]:
        """
        The session parameter encourages the caller to call this function within DB session.

        Verifies the auth with the third party.
        Throws an exception if the access token is expired.
        Although we have the refresh token, the client will have to refresh the token themselves and
        retry the request. Otherwise the refresh token serves no purpose.
        """
        match self.auth_provider:
            case AuthProvider.google:
                if not self.refresh_token:
                    raise MissingOAuthCredentialsError("AccountOrm refresh token")

                credentials = eave.core.internal.oauth.google.get_oauth_credentials(
                    access_token=self.access_token, refresh_token=self.refresh_token
                )
                eave.core.internal.oauth.google.get_userinfo(credentials=credentials)
                self.set_tokens(
                    session=session, access_token=credentials.token, refresh_token=credentials.refresh_token
                )
                return True
            case _:
                raise

    async def refresh_oauth_token(self, session: AsyncSession, ctx: LogContext | None = None) -> typing.Literal[True]:
        """
        The session parameter encourages the caller to call this function within DB session.
        """
        if not self.refresh_token:
            raise MissingOAuthCredentialsError("account refresh token")

        match self.auth_provider:
            case AuthProvider.google:
                # The google client automatically refreshes the access token and updates the Credentials object,
                # So we always update the token values in the database any time the Credentials are used.
                # See https://github.com/googleapis/google-auth-library-python-httplib2/blob/f5ed19e7e5b2b8959d16b2b1e6a6bdd6ff0c0ef6/google_auth_httplib2.py#L151-L152
                await self.verify_oauth_or_exception(session=session, ctx=ctx)
                return True

            case _:
                raise  # TODO: Better error reporting. This case should never be reached though.

    async def get_team(self, session: AsyncSession) -> TeamOrm:
        team = await TeamOrm.one_or_exception(session=session, team_id=self.team_id)
        return team

    @property
    def api_model(self) -> AuthenticatedAccount:
        return AuthenticatedAccount.from_orm(self)
