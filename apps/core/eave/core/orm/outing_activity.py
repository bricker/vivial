from datetime import UTC, datetime
from typing import Self
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eave.core.orm.outing import OutingOrm
from eave.core.orm.util.constants import OnDeleteOption
from eave.core.orm.util.mixins import TimedEventMixin
from eave.core.orm.util.user_defined_column_types import ActivitySourceColumnType
from eave.core.shared.enums import ActivitySource

from .base import Base


class OutingActivityOrm(Base, TimedEventMixin):
    """Pivot table between `outings` and activity sources"""

    __tablename__ = "outing_activities"
    __table_args__ = (
        PrimaryKeyConstraint("outing_id", "source_id", name="outing_activity_pivot_pk"),
    )

    outing_id: Mapped[UUID] = mapped_column(ForeignKey(f"{OutingOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE))
    source_id: Mapped[str] = mapped_column()
    """ID of activity in remote table"""
    source: Mapped[ActivitySource] = mapped_column(type_=ActivitySourceColumnType())
    """ActivitySource enum value"""
    headcount: Mapped[int] = mapped_column()

    @classmethod
    def build(
        cls,
        *,
        outing_id: UUID,
        source_id: str,
        source: ActivitySource,
        start_time_utc: datetime,
        timezone: ZoneInfo,
        headcount: int,
    ) -> "OutingActivityOrm":
        obj = OutingActivityOrm(
            outing_id=outing_id,
            source_id=source_id,
            source=source,
            start_time_utc=start_time_utc.astimezone(UTC),
            timezone=timezone,
            headcount=headcount,
        )

        return obj

    @classmethod
    async def get_one_by_outing_id(cls, session: AsyncSession, outing_id: UUID) -> Self:
        lookup = cls.select().where(cls.outing_id == outing_id)
        result = (await session.scalars(lookup)).one()
        return result
