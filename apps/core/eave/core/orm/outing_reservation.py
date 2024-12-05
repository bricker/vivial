from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from eave.core.graphql.types.restaurant import RestaurantSource

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
    """RestaurantSource enum value"""
    reservation_start_time: Mapped[datetime] = mapped_column()
    headcount: Mapped[int] = mapped_column(name="num_attendees")
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    def build(
        cls,
        *,
        outing_id: UUID,
        reservation_id: str,
        reservation_source: RestaurantSource,
        reservation_start_time: datetime,
        headcount: int,
    ) -> "OutingReservationOrm":
        obj = OutingReservationOrm(
            outing_id=outing_id,
            reservation_id=reservation_id,
            reservation_source=reservation_source,
            reservation_start_time=reservation_start_time,
            headcount=headcount,
        )

        return obj

    @classmethod
    async def get_one_by_outing_id(cls, session: AsyncSession, outing_id: UUID) -> Self:
        lookup = cls.select().where(cls.outing_id == outing_id)
        result = (await session.scalars(lookup)).one()
        return result
