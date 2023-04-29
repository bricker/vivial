from ctypes import ArgumentError
from datetime import datetime
from typing import NotRequired, Optional, Self, Tuple, TypedDict, Unpack
from uuid import UUID

from sqlalchemy import Index, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from . import UUID_DEFAULT_EXPR, Base, make_team_composite_pk, make_team_fk


class SlackInstallationOrm(Base):
    __tablename__ = "slack_sources"
    __table_args__ = (
        make_team_composite_pk(),
        make_team_fk(),
        Index(
            "slack_team_id_eave_team_id",
            "team_id",
            "slack_team_id",
            unique=True,
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    """eave TeamOrm id"""
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    slack_team_id: Mapped[str] = mapped_column(unique=True, index=True)
    """team[id] from here: https://api.slack.com/methods/oauth.v2.access#examples"""
    # bot identification data for authorizing slack api calls
    bot_token: Mapped[str] = mapped_column()
    bot_id: Mapped[str] = mapped_column()
    bot_user_id: Mapped[Optional[str]] = mapped_column(server_default=None)
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: UUID,
        slack_team_id: str,
        bot_token: str,
        bot_id: str,
        bot_user_id: Optional[str] = None,
    ) -> Self:
        obj = cls(
            team_id=team_id,
            slack_team_id=slack_team_id,
            bot_token=bot_token,
            bot_id=bot_id,
            bot_user_id=bot_user_id,
        )
        session.add(obj)
        return obj

    class _selectparams(TypedDict):
        slack_team_id: NotRequired[str]
        team_id: NotRequired[UUID]

    @classmethod
    def _build_select(cls, **kwargs: Unpack[_selectparams]) -> Select[Tuple[Self]]:
        lookup = select(cls).limit(1)
        slack_team_id = kwargs.get("slack_team_id")
        eave_team_id = kwargs.get("team_id")
        if not slack_team_id and not eave_team_id:
            raise ArgumentError("at least one parameter is required")
        if slack_team_id:
            lookup = lookup.where(cls.slack_team_id == slack_team_id)
        if eave_team_id:
            lookup = lookup.where(cls.team_id == eave_team_id)

        assert lookup.whereclause is not None
        return lookup

    @classmethod
    async def one_or_none(cls, session: AsyncSession, **kwargs: Unpack[_selectparams]) -> Optional[Self]:
        lookup = cls._build_select(**kwargs)
        result = (await session.scalars(lookup)).one_or_none()
        return result

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, **kwargs: Unpack[_selectparams]) -> Self:
        lookup = cls._build_select(**kwargs)
        result = (await session.scalars(lookup)).one()
        return result
