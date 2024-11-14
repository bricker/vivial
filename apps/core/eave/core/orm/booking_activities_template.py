from datetime import datetime
from uuid import UUID

from geoalchemy2 import Geography, WKBElement
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.lib.geo import GeoPoint, SpatialReferenceSystemId
from eave.core.orm.address_types import PostgisStdaddr, PostgisStdaddrColumnType

from .base import Base
from .util import PG_UUID_EXPR


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

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    booking_id: Mapped[UUID] = mapped_column()
    activity_name: Mapped[str] = mapped_column()
    activity_start_time: Mapped[datetime] = mapped_column()
    num_attendees: Mapped[int] = mapped_column()
    external_booking_link: Mapped[str | None] = mapped_column()
    """HTTP link to site for manual booking (possibly affialate), if available"""
    address: Mapped[PostgisStdaddr] = mapped_column(type_=PostgisStdaddrColumnType())
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
        activity_name: str,
        activity_start_time: datetime,
        num_attendees: int,
        external_booking_link: str | None,
        address: PostgisStdaddr,
        lat: float,
        lon: float,
    ) -> "BookingActivityTemplateOrm":
        obj = BookingActivityTemplateOrm(
            booking_id=booking_id,
            activity_name=activity_name,
            activity_start_time=activity_start_time,
            num_attendees=num_attendees,
            external_booking_link=external_booking_link,
            address=address,
            coordinates=GeoPoint(lat=lat, lon=lon).geoalchemy_shape(),
        )

        return obj
