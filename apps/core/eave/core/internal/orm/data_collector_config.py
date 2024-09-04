from datetime import datetime
from typing import Self
from uuid import UUID

from eave.stdlib.core_api.models.data_collector_config import DataCollectorConfig
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

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

    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @property
    def api_model(self) -> DataCollectorConfig:
        return DataCollectorConfig.from_orm(self)

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
