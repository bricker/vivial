from datetime import datetime
from typing import Optional, Self, Tuple, TypedDict, Unpack
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

import eave.stdlib.util
from eave.stdlib.core_api.models.team import AnalyticsTeam, Team

from .base import Base
from .util import UUID_DEFAULT_EXPR


class TeamOrm(Base):
    __tablename__ = "teams"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=UUID_DEFAULT_EXPR)
    name: Mapped[str]
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        name: str,
    ) -> Self:
        obj = cls(
            name=name,
        )
        session.add(obj)
        await session.flush()
        return obj

    @property
    def api_model(self) -> Team:
        return Team.from_orm(self)

    @property
    def analytics_model(self) -> AnalyticsTeam:
        return AnalyticsTeam.from_orm(self)

    class QueryParams(TypedDict):
        team_id: UUID | str

    @classmethod
    def query(cls, **kwargs: Unpack[QueryParams]) -> Select[Tuple[Self]]:
        team_id = eave.stdlib.util.ensure_uuid(kwargs["team_id"])
        lookup = select(cls).where(cls.id == team_id)
        return lookup

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, **kwargs: Unpack[QueryParams]) -> Self:
        lookup = cls.query(**kwargs).limit(1)
        result = (await session.scalars(lookup)).one()
        return result

    @classmethod
    async def one_or_none(cls, session: AsyncSession, **kwargs: Unpack[QueryParams]) -> Self | None:
        lookup = cls.query(**kwargs).limit(1)
        result = await session.scalar(lookup)
        return result
