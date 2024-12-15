from uuid import UUID

from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint, Table
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eave.core.lib.address import Address
from eave.core.orm.image import ImageOrm
from eave.core.orm.util.mixins import CoordinatesMixin, GetOneByIdMixin
from eave.core.orm.util.user_defined_column_types import AddressFieldsColumnType
from eave.core.shared.geo import GeoPoint

from .base import Base
from .util.constants import PG_UUID_EXPR, OnDeleteOption

_activity_images_join_table = Table(
    "activity_images",
    Base.metadata,
    Column("activity_id", ForeignKey("activities.id", ondelete=OnDeleteOption.CASCADE.value)),
    Column("image_id", ForeignKey(f"{ImageOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE.value)),
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
    address: Mapped[Address] = mapped_column(type_=AddressFieldsColumnType())
    is_bookable: Mapped[bool] = mapped_column()
    booking_url: Mapped[str | None] = mapped_column()

    images: Mapped[list[ImageOrm]] = relationship(secondary=_activity_images_join_table, lazy="selectin")
    ticket_types: Mapped[list["TicketTypeOrm"]] = relationship(lazy="selectin", back_populates="activity")

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        title: str,
        description: str,
        coordinates: GeoPoint,
        activity_category_id: UUID,
        duration_minutes: int,
        availability: str,
        address: Address,
        is_bookable: bool,
        booking_url: str | None,
    ) -> None:
        self.title = title
        self.description = description
        self.coordinates = coordinates.geoalchemy_shape()
        self.activity_category_id = activity_category_id
        self.duration_minutes = duration_minutes
        self.availability = availability
        self.address = address
        self.is_bookable = is_bookable
        self.booking_url = booking_url

        if session:
            session.add(self)


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
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    base_cost_cents: Mapped[int] = mapped_column()
    service_fee_cents: Mapped[int] = mapped_column()
    tax_percentage: Mapped[float] = mapped_column()

    activity_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{ActivityOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE.value)
    )
    activity: Mapped[ActivityOrm] = relationship(lazy="selectin", back_populates="ticket_types")

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        activity: ActivityOrm,
        title: str,
        description: str,
        base_cost_cents: int,
        service_fee_cents: int,
        tax_percentage: float,
    ) -> None:
        self.activity = activity
        self.title = title
        self.description = description
        self.base_cost_cents = base_cost_cents
        self.service_fee_cents = service_fee_cents
        self.tax_percentage = tax_percentage

        if session:
            session.add(self)
