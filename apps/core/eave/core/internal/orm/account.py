from . import UUID_DEFAULT_EXPR, Base, make_team_composite_pk, make_team_fk


import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.operations as eave_ops
import eave.stdlib.util as eave_util
from sqlalchemy import Index, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column


import uuid
from datetime import datetime
from typing import NotRequired, Optional, Self, Tuple, TypedDict, Unpack
from uuid import UUID


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
    auth_provider: Mapped[eave_models.AuthProvider] = mapped_column()
    """3rd party login provider"""
    auth_id: Mapped[str] = mapped_column()
    """userid from 3rd party auth_provider"""
    oauth_token: Mapped[str] = mapped_column()
    """access token from 3rd party"""
    refresh_token: Mapped[Optional[str]] = mapped_column(server_default=None)
    """refresh token from 3rd party"""
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(cls, session: AsyncSession, team_id: UUID, auth_provider: eave_models.AuthProvider, auth_id: str, oauth_token: str, refresh_token: Optional[str]) -> Self:
        obj = cls(
            team_id=team_id,
            auth_provider=auth_provider,
            auth_id=auth_id,
            oauth_token=oauth_token,
            refresh_token=refresh_token,
        )

        session.add(obj)
        await session.flush()
        return obj

    class _selectparams(TypedDict):
        id: NotRequired[uuid.UUID]
        team_id: NotRequired[uuid.UUID]
        auth_provider: NotRequired[eave_models.AuthProvider]
        auth_id: NotRequired[str]

    @classmethod
    def _build_select(cls, **kwargs: Unpack[_selectparams]) -> Select[Tuple[Self]]:
        lookup = select(cls).limit(1)

        id = kwargs.get("id")
        team_id = kwargs.get("team_id")
        assert eave_util.xnor(id, team_id)

        auth_provider = kwargs.get("auth_provider")
        auth_id = kwargs.get("auth_id")
        assert eave_util.xnor(auth_provider, auth_id)

        if id and team_id:
            lookup = lookup.where(cls.id == id).where(cls.team_id == team_id)

        if auth_provider and auth_id:
            lookup = (
                lookup
                .where(cls.auth_provider == auth_provider)
                .where(cls.auth_id == auth_id)
            )

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