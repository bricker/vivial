from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import UUID

from eave.stdlib.typing import NOT_SET, NotSet
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .util import PG_UUID_EXPR


class BookingReservationTemplateOrm(Base):
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
        ForeignKeyConstraint(
            ["booking_id"],
            ["bookings.id"],
            ondelete="CASCADE",
            name="booking_id_booking_reservation_template_fk",
        ),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    booking_id: Mapped[UUID] = mapped_column()
    reservation_name: Mapped[str] = mapped_column()
    reservation_start_time: Mapped[datetime] = mapped_column()
    num_attendees: Mapped[int] = mapped_column()
    external_booking_link: Mapped[str | None] = mapped_column()
    """HTTP link to site for manual booking (possibly affialate), if available"""
    reservation_location_address1: Mapped[str] = mapped_column()
    reservation_location_address2: Mapped[str] = mapped_column()
    reservation_location_city: Mapped[str] = mapped_column()
    reservation_location_region: Mapped[str] = mapped_column()
    """Name of region. e.g. state, province, territory, prefecture"""
    reservation_location_country: Mapped[str] = mapped_column()
    reservation_location_latitude: Mapped[float] = mapped_column()
    reservation_location_longitude: Mapped[float] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    def build(
        cls,
        *,
        booking_id: UUID,
        reservation_name: str,
        reservation_start_time: datetime,
        num_attendees: int,
        external_booking_link: str | None,
        reservation_location_address1: str,
        reservation_location_address2: str,
        reservation_location_city: str,
        reservation_location_region: str,
        reservation_location_country: str,
        reservation_location_latitude: float,
        reservation_location_longitude: float,
    ) -> Self:
        obj = cls(
            booking_id=booking_id,
            reservation_name=reservation_name,
            reservation_start_time=reservation_start_time,
            num_attendees=num_attendees,
            external_booking_link=external_booking_link,
            reservation_location_address1=reservation_location_address1,
            reservation_location_address2=reservation_location_address2,
            reservation_location_city=reservation_location_city,
            reservation_location_region=reservation_location_region,
            reservation_location_country=reservation_location_country,
            reservation_location_latitude=reservation_location_latitude,
            reservation_location_longitude=reservation_location_longitude,
        )

        return obj
