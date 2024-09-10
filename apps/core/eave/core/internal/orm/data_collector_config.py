from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import Select, String, func, select
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.core_api.models.data_collector_config import DataCollectorConfig

from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_composite_pk, make_team_fk


class DataCollectorConfigOrm(Base):
    __tablename__ = "data_collector_configs"
    __table_args__ = (
        make_team_composite_pk(table_name="data_collector_configs"),
        make_team_fk(),
    )

    team_id: Mapped[UUID] = mapped_column(unique=True)
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    primary_key_patterns: Mapped[list[str]] = mapped_column(
        type_=ARRAY(item_type=String, dimensions=1),
        default=lambda: [
            r"^id$",
            r"^uid$",
        ],
    )
    """List of regex matchers used for identifying pk values we wish to track"""
    foreign_key_patterns: Mapped[list[str]] = mapped_column(
        type_=ARRAY(item_type=String, dimensions=1),
        default=lambda: [
            # We don't want to capture fields that end in "id" but aren't foreign keys, like "kool_aid" or "mermaid".
            # We therefore make an assumption that anything ending in "id" with SOME delimeter is a foreign key.
            r".[_-]id$",  # delimeter = {_, -} Only matches when "id" is lower-case.
            r".I[Dd]$",  # delimeter = capital "I" (eg UserId). This also handles underscores/hyphens when the "I" is capital.
        ],
    )
    """List of regex matchers used for identifying fk values we wish to track"""
    user_table_name_patterns: Mapped[list[str]] = mapped_column(
        type_=ARRAY(item_type=String, dimensions=1),
        default=lambda: [
            r"users?$",
            r"accounts?$",
            r"customers?$",
        ],
    )
    """List of regex matchers used for identifying a users db table we may track keys from"""
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
