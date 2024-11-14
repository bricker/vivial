from datetime import datetime
from typing import Self
from uuid import UUID

from geoalchemy2 import WKBElement
from geoalchemy2.types import Geography
from sqlalchemy import PrimaryKeyConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.lib.geo import GeoPoint, SpatialReferenceSystemId
from eave.core.orm.address_types import PostgisStdaddr, PostgisStdaddrColumnType

from .base import Base
from .util import PG_UUID_EXPR


class ActivityOrm(Base):
    __tablename__ = "activities"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    coordinates: Mapped[WKBElement] = mapped_column(
        type_=Geography(geometry_type="POINT", srid=SpatialReferenceSystemId.LAT_LON)
    )
    subcategory_id: Mapped[UUID] = mapped_column()
    duration_minutes: Mapped[int] = mapped_column()
    availability: Mapped[str] = mapped_column()
    address: Mapped[PostgisStdaddr] = mapped_column(type_=PostgisStdaddrColumnType())
    is_bookable: Mapped[bool] = mapped_column()
    booking_url: Mapped[str | None] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    def build(
        cls,
        *,
        title: str,
        description: str,
        lat: float,
        lon: float,
        subcategory_id: UUID,
        duration_minutes: int,
        availability: str,
        address: PostgisStdaddr,
        is_bookable: bool,
        booking_url: str | None,
    ) -> "ActivityOrm":
        return ActivityOrm(
            title=title,
            description=description,
            coordinates=GeoPoint(lat=lat, lon=lon).geoalchemy_shape(),
            subcategory_id=subcategory_id,
            duration_minutes=duration_minutes,
            availability=availability,
            address=address,
            is_bookable=is_bookable,
            booking_url=booking_url,
        )
