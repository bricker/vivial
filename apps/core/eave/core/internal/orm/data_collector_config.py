from datetime import datetime
from typing import Self
from uuid import UUID

from eave.stdlib.core_api.models.data_collector_config import DataCollectorConfig
from sqlalchemy import Select, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY

from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_composite_pk, make_team_fk


class DataCollectorConfigOrm(Base):
    __tablename__ = "data_collector_configs"
    __table_args__ = (
        make_team_composite_pk(table_name="data_collector_configs"),
        make_team_fk(),
    )

    # TODO add unique constraint on team_id to prevent multi entries? how many current tables should have one but dont'?
    # or is relying on one_or_exception enough?
    team_id: Mapped[UUID] = mapped_column(unique=True)
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    # TODO: move default values from collector core
    id_matchers: Mapped[list[str]] = mapped_column(
        type_=ARRAY(item_type=String, dimensions=1), default=lambda: ["dummy regex"]
    )
    """List of regex matchers used for identifying values we wish to track"""
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @property
    def api_model(self) -> DataCollectorConfig:
        return DataCollectorConfig.from_orm(self)

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: UUID | None,
    ) -> Self:
        obj = cls(
            team_id=team_id,
        )
        session.add(obj)
        await session.flush()
        return obj

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, team_id: UUID) -> Self:
        lookup = cls.query(team_id=team_id).limit(1)
        result = (await session.scalars(lookup)).one()
        return result

    @classmethod
    async def one_or_none(cls, session: AsyncSession, team_id: UUID) -> Self | None:
        lookup = cls.query(team_id=team_id).limit(1)
        result = await session.scalar(lookup)
        return result

    @classmethod
    def query(cls, team_id: UUID) -> Select[tuple[Self]]:
        lookup = select(cls)
        lookup.where(cls.team_id == team_id)
        return lookup
