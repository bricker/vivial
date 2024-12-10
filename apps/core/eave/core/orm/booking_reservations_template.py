from datetime import UTC, datetime
from typing import Self
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.lib.geo import GeoPoint
from eave.core.orm.booking import BookingOrm
from eave.core.orm.util.mixins import CoordinatesMixin, TimedEventMixin
from eave.core.orm.util.user_defined_column_types import (
    AddressColumnType,
    RestaurantSourceColumnType,
)
from eave.core.shared.address import Address
from eave.core.shared.enums import RestaurantSource

from .base import Base
from .util.constants import PG_UUID_EXPR, OnDeleteOption


class BookingReservationTemplateOrm(Base, TimedEventMixin, CoordinatesMixin):
    """Editable template for a booked reservation.
    Edits are visible to other accounts part of the same booking, but
    not other bookings created from the same outing. Also does not
    mutate the reservation this template cloned its source data from."""

    __tablename__ = "booking_reservation_templates"
    __table_args__ = (
        PrimaryKeyConstraint(
            "booking_id",
            "id",
            name="booking_reservation_template_pk",
        ),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    booking_id: Mapped[UUID] = mapped_column(ForeignKey(f"{BookingOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE))
    source_id: Mapped[str] = mapped_column()
    source: Mapped[RestaurantSource] = mapped_column(type_=RestaurantSourceColumnType())
    """RestaurantSource enum value"""
    name: Mapped[str] = mapped_column()
    photo_uri: Mapped[str | None] = mapped_column()
    headcount: Mapped[int] = mapped_column()
    external_booking_link: Mapped[str | None] = mapped_column()
    """HTTP link to site for manual booking (possibly affiliate), if available"""
    address: Mapped[Address] = mapped_column(type_=AddressColumnType())

    @classmethod
    def build(
        cls,
        *,
        booking_id: UUID,
        source: RestaurantSource,
        source_id: str,
        name: str,
        start_time_utc: datetime,
        timezone: ZoneInfo,
        photo_uri: str | None,
        headcount: int,
        external_booking_link: str | None,
        address: Address,
        lat: float,
        lon: float,
    ) -> "BookingReservationTemplateOrm":
        obj = BookingReservationTemplateOrm(
            booking_id=booking_id,
            source=source,
            source_id=source_id,
            name=name,
            start_time_utc=start_time_utc.astimezone(UTC),
            timezone=timezone,
            photo_uri=photo_uri,
            headcount=headcount,
            external_booking_link=external_booking_link,
            address=address,
            coordinates=GeoPoint(lat=lat, lon=lon).geoalchemy_shape(),
        )

        return obj

    @classmethod
    async def get_one(cls, session: AsyncSession, *, booking_id: UUID, uid: UUID) -> Self:
        return await session.get_one(cls, (booking_id, uid))
