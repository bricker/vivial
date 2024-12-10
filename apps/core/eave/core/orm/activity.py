from typing import Self
from uuid import UUID

from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint, ScalarResult, Select, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eave.core.lib.geo import GeoPoint
from eave.core.orm.image import ImageOrm
from eave.core.orm.util.mixins import CoordinatesMixin, GetOneByIdMixin
from eave.core.orm.util.user_defined_column_types import AddressColumnType
from eave.core.shared.address import Address
from eave.stdlib.typing import NOT_SET

from .base import Base
from .util.constants import PG_UUID_EXPR, OnDeleteOption

_activity_images_join_table = Table(
    "activity_images",
    Base.metadata,
    Column("activity_id", ForeignKey("activities.id", ondelete=OnDeleteOption.CASCADE)),
    Column("image_id", ForeignKey(f"{ImageOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE)),
)

class ActivityOrm(Base, CoordinatesMixin, GetOneByIdMixin):
    __tablename__ = "activities"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    activity_category_id: Mapped[UUID] = mapped_column()
    duration_minutes: Mapped[int] = mapped_column()
    availability: Mapped[str] = mapped_column()
    address: Mapped[Address] = mapped_column(type_=AddressColumnType())
    is_bookable: Mapped[bool] = mapped_column()
    booking_url: Mapped[str | None] = mapped_column()

    images: Mapped[list[ImageOrm]] = relationship(secondary=_activity_images_join_table, lazy="selectin")

    def __init__(
        self,
        *,
        title: str,
        description: str,
        lat: float,
        lon: float,
        activity_category_id: UUID,
        duration_minutes: int,
        availability: str,
        address: Address,
        is_bookable: bool,
        booking_url: str | None,
    ) -> None:
        self.title = title
        self.description = description
        self.coordinates = GeoPoint(lat=lat, lon=lon).geoalchemy_shape()
        self.activity_category_id = activity_category_id
        self.duration_minutes = duration_minutes
        self.availability = availability
        self.address = address
        self.is_bookable = is_bookable
        self.booking_url = booking_url


class TicketTypeOrm(Base, GetOneByIdMixin):
    __tablename__ = "ticket_types"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        ForeignKeyConstraint(
            columns=["activity_id"],
            refcolumns=["activities.id"],
            ondelete="CASCADE",
        ),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    activity_id: Mapped[UUID] = mapped_column(ForeignKey(f"{ActivityOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE))
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    base_cost_cents: Mapped[int] = mapped_column()
    service_fee_cents: Mapped[int] = mapped_column()
    tax_percentage: Mapped[float] = mapped_column()
