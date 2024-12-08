from datetime import UTC, datetime, tzinfo
from uuid import UUID
from zoneinfo import ZoneInfo

from geoalchemy2 import Geography, WKBElement
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, func, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import TIMESTAMP

from eave.core.lib.geo import GeoPoint, SpatialReferenceSystemId
from eave.core.orm.util.mixins import CoordinatesMixin, TimedEventMixin
from eave.core.orm.util.user_defined_column_types import ActivitySourceColumnType, AddressColumnType, StrEnumColumnType, ZoneInfoColumnType
from eave.core.shared.address import Address
from eave.core.shared.enums import ActivitySource

from .base import Base
from .util.constants import PG_UUID_EXPR


class BookingActivityTemplateOrm(Base, TimedEventMixin, CoordinatesMixin):
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
    source_id: Mapped[str] = mapped_column()
    source: Mapped[ActivitySource] = mapped_column(type_=ActivitySourceColumnType())
    """ActivitySource enum value"""
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
        source: ActivitySource,
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
    ) -> "BookingActivityTemplateOrm":
        obj = BookingActivityTemplateOrm(
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
