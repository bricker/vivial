from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .util import UUID_DEFAULT_EXPR


class BookingActivityTemplateOrm(Base):
    """Editable template for a booked activity.
    Edits are visible to other accounts part of the same booking, but
    not other bookings created from the same outing. Also does not
    mutate the activity this template cloned its source data from."""

    __tablename__ = "booking_activity_templates"
    __table_args__ = (
        PrimaryKeyConstraint(
            "booking_id",
            "id",
            name="booking_activity_template_pk",
        ),
        ForeignKeyConstraint(
            ["booking_id"],
            ["bookings.id"],
            ondelete="CASCADE",
            name="booking_id_booking_activity_template_fk",
        ),
    )

    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    booking_id: Mapped[UUID] = mapped_column()
    activity_name: Mapped[str] = mapped_column()
    activity_start_time: Mapped[datetime] = mapped_column()
    num_attendees: Mapped[int] = mapped_column()
    external_booking_link: Mapped[str | None] = mapped_column()
    """HTTP link to site for manual booking (possibly affialate), if available"""
    activity_location_address1: Mapped[str] = mapped_column()
    activity_location_address2: Mapped[str] = mapped_column()
    activity_location_city: Mapped[str] = mapped_column()
    activity_location_region: Mapped[str] = mapped_column()
    """Name of region. e.g. state, province, territory, prefecture"""
    activity_location_country: Mapped[str] = mapped_column()
    activity_location_latitude: Mapped[float] = mapped_column()
    activity_location_longitude: Mapped[float] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        booking_id: UUID,
        activity_name: str,
        activity_start_time: datetime,
        num_attendees: int,
        external_booking_link: str | None,
        activity_location_address1: str,
        activity_location_address2: str,
        activity_location_city: str,
        activity_location_region: str,
        activity_location_country: str,
        activity_location_latitude: float,
        activity_location_longitude: float,
    ) -> Self:
        obj = cls(
            booking_id=booking_id,
            activity_name=activity_name,
            activity_start_time=activity_start_time,
            num_attendees=num_attendees,
            external_booking_link=external_booking_link,
            activity_location_address1=activity_location_address1,
            activity_location_address2=activity_location_address2,
            activity_location_city=activity_location_city,
            activity_location_region=activity_location_region,
            activity_location_country=activity_location_country,
            activity_location_latitude=activity_location_latitude,
            activity_location_longitude=activity_location_longitude,
        )

        session.add(obj)
        await session.flush()
        return obj

    @dataclass
    class QueryParams:
        booking_id: UUID | None = None
        id: UUID | None = None

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[tuple[Self]]:
        lookup = select(cls)

        if params.booking_id is not None:
            lookup = lookup.where(cls.booking_id == params.booking_id)

        if params.id is not None:
            lookup = lookup.where(cls.id == params.id)

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
