from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.core_api.models.enums import ReservationSource

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
    async def create(
        cls,
        session: AsyncSession,
        outing_id: UUID,
        reservation_id: str,
        reservation_source: ReservationSource,
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

        session.add(obj)
        await session.flush()
        return obj

    @dataclass
    class QueryParams:
        outing_id: UUID | None = None
        reservation_id: str | None = None

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[tuple[Self]]:
        lookup = select(cls)

        if params.outing_id is not None:
            lookup = lookup.where(cls.outing_id == params.outing_id)

        if params.reservation_id is not None:
            lookup = lookup.where(cls.reservation_id == params.reservation_id)

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup

    @classmethod
    async def query(cls, session: AsyncSession, params: QueryParams) -> Sequence[Self]:
        lookup = cls._build_query(params=params)
        result = (await session.scalars(lookup)).all()
        return result

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, params: QueryParams) -> Self:
        lookup = cls._build_query(params=params)
        result = (await session.scalars(lookup)).one()
        return result

    @classmethod
    async def one_or_none(cls, session: AsyncSession, params: QueryParams) -> Self | None:
        lookup = cls._build_query(params=params)
        result = await session.scalar(lookup)
        return result
