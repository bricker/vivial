from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class OutingActivityOrm(Base):
    """Pivot table between `outings` and `activities` tables. (`activities` is a remote dataset)"""

    __tablename__ = "outing_activities"
    __table_args__ = (
        PrimaryKeyConstraint("outing_id", "activity_id", name="outing_activity_pivot_pk"),
        ForeignKeyConstraint(
            ["outing_id"],
            ["outings.id"],
            ondelete="CASCADE",
            name="outing_id_activity_pivot_fk",
        ),
        # no fk for activity_id bcus it's a remote db
    )

    outing_id: Mapped[UUID] = mapped_column()
    activity_id: Mapped[str] = mapped_column()
    """ID of activity in remote table"""
    activity_source: Mapped[str] = mapped_column()
    """EventSource enum value"""
    activity_start_time: Mapped[datetime] = mapped_column()
    num_attendees: Mapped[int] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    def build(
        cls,
        *,
        outing_id: UUID,
        activity_id: str,
        activity_source: EventSource,
        activity_start_time: datetime,
        num_attendees: int,
    ) -> Self:
        obj = cls(
            outing_id=outing_id,
            activity_id=activity_id,
            activity_start_time=activity_start_time,
            activity_source=activity_source,
            num_attendees=num_attendees,
        )

        return obj
