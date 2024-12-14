from uuid import UUID

from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.lib.geo import GeoPoint
from eave.core.orm.util.mixins import CoordinatesMixin
from eave.core.orm.util.user_defined_column_types import AddressColumnType
from eave.core.shared.address import Address

from .base import Base
from .util.constants import PG_UUID_EXPR


class ActivityOrm(Base, CoordinatesMixin):
    __tablename__ = "activities"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    activity_category_group_id: Mapped[UUID] = mapped_column()
    duration_minutes: Mapped[int] = mapped_column()
    availability: Mapped[str] = mapped_column()
    address: Mapped[Address] = mapped_column(type_=AddressColumnType())
    is_bookable: Mapped[bool] = mapped_column()
    booking_url: Mapped[str | None] = mapped_column()

    @classmethod
    def build(
        cls,
        *,
        title: str,
        description: str,
        lat: float,
        lon: float,
        activity_category_group_id: UUID,
        duration_minutes: int,
        availability: str,
        address: Address,
        is_bookable: bool,
        booking_url: str | None,
    ) -> "ActivityOrm":
        return ActivityOrm(
            title=title,
            description=description,
            coordinates=GeoPoint(lat=lat, lon=lon).geoalchemy_shape(),
            activity_category_group_id=activity_category_group_id,
            duration_minutes=duration_minutes,
            availability=availability,
            address=address,
            is_bookable=is_bookable,
            booking_url=booking_url,
        )
