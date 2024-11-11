from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import UUID

from eave.stdlib.typing import NOT_GIVEN, NotGiven
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.outing.models.sources import RestaurantSource

from .base import Base


class OutingReservationOrm(Base):
    """Pivot table between `outings` and `reservations` tables. (`reservations` is a remote dataset)"""

    __tablename__ = "outing_reservations"
    __table_args__ = (
        PrimaryKeyConstraint("outing_id", "reservation_id", name="outing_reservation_pivot_pk"),
        ForeignKeyConstraint(
            ["outing_id"],
            ["outings.id"],
            ondelete="CASCADE",
            name="outing_id_reservation_pivot_fk",
        ),
        # no fk for reservation_id bcus it's a remote db
    )

    outing_id: Mapped[UUID] = mapped_column()
    reservation_id: Mapped[str] = mapped_column()
    """ID of reservation in remote table"""
    reservation_source: Mapped[str] = mapped_column()
    """ReservationSource enum value"""
    reservation_start_time: Mapped[datetime] = mapped_column()
    num_attendees: Mapped[int] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def build(
        cls,
        *,
        outing_id: UUID,
        reservation_id: str,
        reservation_source: RestaurantSource,
        reservation_start_time: datetime,
        num_attendees: int,
    ) -> Self:
        obj = cls(
            outing_id=outing_id,
            reservation_id=reservation_id,
            reservation_source=reservation_source,
            reservation_start_time=reservation_start_time,
            num_attendees=num_attendees,
        )

        return obj
