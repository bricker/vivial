import typing
import uuid
from datetime import datetime
from typing import Dict, NotRequired, Optional, Self, Tuple, TypedDict, Unpack
from uuid import UUID

from .util import make_team_composite_pk, make_team_fk
from .base import Base
from .team import TeamOrm

import eave.core.internal.oauth.atlassian
import eave.core.internal.oauth.google
import eave.core.internal.oauth.slack
import eave.stdlib.core_api
import eave.stdlib
import slack_sdk.errors
from sqlalchemy import Index, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from .util import UUID_DEFAULT_EXPR


class AccountOrm(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        make_team_composite_pk(),
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
            "oauth_token",
            unique=True,
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    visitor_id: Mapped[Optional[UUID]] = mapped_column()
    opaque_utm_params: Mapped[Optional[eave.stdlib.util.JsonObject]] = mapped_column(JSONB)
    """Opaque, JSON-encoded utm params."""
    auth_provider: Mapped[eave.stdlib.core_api.enums.AuthProvider] = mapped_column()
    """3rd party login provider"""
    auth_id: Mapped[str] = mapped_column()
    """userid from 3rd party auth_provider"""
    access_token: Mapped[str] = mapped_column("oauth_token") # This field was renamed from "oauth_token" to "access_token"
    """access token from 3rd party"""
    refresh_token: Mapped[Optional[str]] = mapped_column(server_default=None)
    """refresh token from 3rd party"""
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: UUID,
        visitor_id: Optional[UUID],
        opaque_utm_params: Optional[eave.stdlib.util.JsonObject],
        auth_provider: eave.stdlib.core_api.enums.AuthProvider,
        auth_id: str,
        access_token: str,
        refresh_token: Optional[str],
    ) -> Self:
        obj = cls(
            team_id=team_id,
            visitor_id=visitor_id,
            opaque_utm_params=opaque_utm_params,
            auth_provider=auth_provider,
            auth_id=auth_id,
            access_token=access_token,
            refresh_token=refresh_token,
        )

        session.add(obj)
        await session.flush()
        return obj

    class _selectparams(TypedDict):
        id: NotRequired[uuid.UUID]
        team_id: NotRequired[uuid.UUID]
        auth_provider: NotRequired[eave.stdlib.core_api.enums.AuthProvider]
        auth_id: NotRequired[str]
        access_token: NotRequired[str]
        refresh_token: NotRequired[str]

    @classmethod
    def _build_select(cls, **kwargs: Unpack[_selectparams]) -> Select[Tuple[Self]]:
        lookup = select(cls).limit(1)

        if id := kwargs.get("id"):
            lookup = lookup.where(cls.id == id)

        if team_id := kwargs.get("team_id"):
            lookup = lookup.where(cls.team_id == team_id)

        if auth_provider := kwargs.get("auth_provider"):
            lookup = lookup.where(cls.auth_provider == auth_provider)

        if auth_id := kwargs.get("auth_id"):
            lookup = lookup.where(cls.auth_id == auth_id)

        if access_token := kwargs.get("access_token"):
            lookup = lookup.where(cls.access_token == access_token)

        if refresh_token := kwargs.get("refresh_token"):
            lookup = lookup.where(cls.refresh_token == refresh_token)

        assert lookup.whereclause is not None
        return lookup

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, **kwargs: Unpack[_selectparams]) -> Self:
        lookup = cls._build_select(**kwargs)
        result = (await session.scalars(lookup)).one()
        return result

    @classmethod
    async def one_or_none(cls, session: AsyncSession, **kwargs: Unpack[_selectparams]) -> Self | None:
        lookup = cls._build_select(**kwargs)
        result = await session.scalar(lookup)
        return result

    async def verify_oauth_or_exception(
        self, session: AsyncSession, log_context: Optional[Dict[str, object]] = None
    ) -> typing.Literal[True]:
        """
        The session parameter encourages the caller to call this function within DB session.

        Verifies the auth with the third party.
        Throws an exception if the access token is expired.
        Although we have the refresh token, the client will have to refresh the token themselves and
        retry the request. Otherwise the refresh token serves no purpose.
        """
        match self.auth_provider:
            case eave.stdlib.core_api.enums.AuthProvider.slack:
                try:
                    await eave.core.internal.oauth.slack.get_userinfo_or_exception(access_token=self.access_token)
                    return True
                except slack_sdk.errors.SlackApiError as e:
                    if e.response.get("error") == "token_expired":
                        raise eave.stdlib.exceptions.AccessTokenExpiredError() from e
                    else:
                        raise e

            case eave.stdlib.core_api.enums.AuthProvider.google:
                if not self.refresh_token:
                    eave.stdlib.logger.error("missing refresh token.", extra=log_context)
                    raise eave.stdlib.exceptions.InvalidAuthError()

                credentials = eave.core.internal.oauth.google.get_oauth_credentials(
                    access_token=self.access_token, refresh_token=self.refresh_token
                )
                eave.core.internal.oauth.google.get_userinfo(credentials=credentials)
                self.access_token = credentials.token
                self.refresh_token = credentials.refresh_token
                return True
            case eave.stdlib.core_api.enums.AuthProvider.atlassian:
                return True
            case _:
                raise

    async def refresh_oauth_token(
        self, session: AsyncSession, log_context: Optional[Dict[str, object]] = None
    ) -> typing.Literal[True]:
        """
        The session parameter encourages the caller to call this function within DB session.
        """
        if not self.refresh_token:
            eave.stdlib.logger.error("missing refresh token.", extra=log_context)
            raise eave.stdlib.exceptions.InvalidAuthError()

        match self.auth_provider:
            case eave.stdlib.core_api.enums.AuthProvider.slack:
                new_tokens = await eave.core.internal.oauth.slack.refresh_access_token(refresh_token=self.refresh_token)
                self.access_token = new_tokens["authed_user"]["access_token"]
                self.refresh_token = new_tokens["authed_user"]["refresh_token"]
                return True

            case eave.stdlib.core_api.enums.AuthProvider.google:
                # The google client automatically refreshes the access token and updates the Credentials object,
                # So we always update the token values in the database any time the Credentials are used.
                await self.verify_oauth_or_exception(session=session, log_context=log_context)
                return True
            case eave.stdlib.core_api.enums.AuthProvider.atlassian:
                return True
            case _:
                raise

    async def get_team(self, session: AsyncSession) -> TeamOrm:
        team = await TeamOrm.one_or_exception(session=session, team_id=self.team_id)
        return team