from datetime import UTC, datetime
from typing import Self
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.graphql.types.restaurant import RestaurantSource
from eave.core.orm.outing import OutingOrm
from eave.core.orm.util.constants import OnDeleteOption
from eave.core.orm.util.mixins import TimedEventMixin
from eave.core.orm.util.user_defined_column_types import (
    RestaurantSourceColumnType,
)

from .base import Base


class OutingReservationOrm(Base, TimedEventMixin):
    """Pivot table between `outings` and `reservations` tables. (`reservations` is a remote dataset)"""

    __tablename__ = "outing_reservations"
    __table_args__ = (
        PrimaryKeyConstraint("outing_id", "source_id", name="outing_reservation_pivot_pk"),
    )

    outing_id: Mapped[UUID] = mapped_column(ForeignKey(f"{OutingOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE))
    source_id: Mapped[str] = mapped_column()
    """ID of reservation in remote table"""
    source: Mapped[RestaurantSource] = mapped_column(type_=RestaurantSourceColumnType())
    """RestaurantSource enum value"""
    headcount: Mapped[int] = mapped_column()

    @classmethod
    def build(
        cls,
        *,
        outing_id: UUID,
        source_id: str,
        source: RestaurantSource,
        start_time_utc: datetime,
        timezone: ZoneInfo,
        headcount: int,
    ) -> "OutingReservationOrm":
        obj = OutingReservationOrm(
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
