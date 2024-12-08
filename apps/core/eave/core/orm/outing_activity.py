from datetime import UTC, datetime, tzinfo
from typing import Self
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, func, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.orm.util.user_defined_column_types import ZoneInfoColumnType
from eave.core.shared.enums import ActivitySource
from eave.core.shared.errors import ValidationError

from .base import Base


class OutingActivityOrm(Base):
    """Pivot table between `outings` and `activities` tables."""

    __tablename__ = "outing_activities"
    __table_args__ = (
        PrimaryKeyConstraint("outing_id", "source_id", name="outing_activity_pivot_pk"),
        ForeignKeyConstraint(
            ["outing_id"],
            ["outings.id"],
            ondelete="CASCADE",
            name="outing_id_activity_pivot_fk",
        ),
    )

    outing_id: Mapped[UUID] = mapped_column()
    source_id: Mapped[str] = mapped_column()
    """ID of activity in remote table"""
    source: Mapped[str] = mapped_column()
    """ActivitySource enum value"""
    start_time_utc: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=True))
    timezone: Mapped[ZoneInfo] = mapped_column(type_=ZoneInfoColumnType())
    headcount: Mapped[int] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

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

    def validate(self) -> list[ValidationError]:
        errors: list[ValidationError] = []

        # try:
        #     ZoneInfo(self.timezone)
        # except ZoneInfoNotFoundError:
        #     errors.append(ValidationError(field="timezone"))

        return errors

    @classmethod
    async def get_one_by_outing_id(cls, session: AsyncSession, outing_id: UUID) -> Self:
        lookup = cls.select().where(cls.outing_id == outing_id)
        result = (await session.scalars(lookup)).one()
        return result

    @property
    def start_time_local(self) -> datetime:
        return self.start_time_utc.astimezone(self.timezone)
