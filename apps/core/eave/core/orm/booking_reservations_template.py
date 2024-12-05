from datetime import datetime
from uuid import UUID

from geoalchemy2 import Geography, WKBElement
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.lib.geo import GeoPoint, SpatialReferenceSystemId
from eave.core.orm.address_types import Address, AddressColumnType
from eave.core.shared.enums import RestaurantSource

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
    source_id: Mapped[str] = mapped_column()
    source: Mapped[str] = mapped_column()
    """RestaurantSource enum value"""
    reservation_name: Mapped[str] = mapped_column()
    reservation_start_time: Mapped[datetime] = mapped_column()
    headcount: Mapped[int] = mapped_column(name="num_attendees")
    external_booking_link: Mapped[str | None] = mapped_column()
    """HTTP link to site for manual booking (possibly affiliate), if available"""
    address: Mapped[Address] = mapped_column(type_=AddressColumnType())
    coordinates: Mapped[WKBElement] = mapped_column(
        type_=Geography(geometry_type="POINT", srid=SpatialReferenceSystemId.LAT_LON)
    )
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    def build(
        cls,
        *,
        booking_id: UUID,
        source: RestaurantSource,
        source_id: str,
        reservation_name: str,
        reservation_start_time: datetime,
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
            reservation_name=reservation_name,
            reservation_start_time=reservation_start_time,
            headcount=headcount,
            external_booking_link=external_booking_link,
            address=address,
            coordinates=GeoPoint(lat=lat, lon=lon).geoalchemy_shape(),
        )

        return obj
