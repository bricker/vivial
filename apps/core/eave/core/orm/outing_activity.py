from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from eave.core.shared.enums import ActivitySource

from .base import Base


class OutingActivityOrm(Base):
    """Pivot table between `outings` and `activities` tables."""

    __tablename__ = "outing_activities"
    __table_args__ = (
        PrimaryKeyConstraint("outing_id", "activity_id", name="outing_activity_pivot_pk"),
        ForeignKeyConstraint(
            ["outing_id"],
            ["outings.id"],
            ondelete="CASCADE",
            name="outing_id_activity_pivot_fk",
        ),
    )

    outing_id: Mapped[UUID] = mapped_column()
    activity_id: Mapped[str] = mapped_column()
    """ID of activity in remote table"""
    activity_source: Mapped[str] = mapped_column()
    """ActivitySource enum value"""
    activity_start_time: Mapped[datetime] = mapped_column()
    headcount: Mapped[int] = mapped_column(name="num_attendees")
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    def build(
        cls,
        *,
        outing_id: UUID,
        activity_id: str,
        activity_source: ActivitySource,
        activity_start_time: datetime,
        headcount: int,
    ) -> "OutingActivityOrm":
        obj = OutingActivityOrm(
            outing_id=outing_id,
            activity_id=activity_id,
            activity_start_time=activity_start_time,
            activity_source=activity_source,
            headcount=headcount,
        )

        return obj

    @classmethod
    async def get_one_by_outing_id(cls, session: AsyncSession, outing_id: UUID) -> Self:
        lookup = cls.select().where(cls.outing_id == outing_id)
        result = (await session.scalars(lookup)).one()
        return result
