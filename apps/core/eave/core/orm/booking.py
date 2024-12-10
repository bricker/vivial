from datetime import UTC, datetime
from typing import TYPE_CHECKING, Self
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Index, PrimaryKeyConstraint, Select, Table, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column, relationship

from eave.core.lib.geo import GeoPoint
from eave.core.orm.account import AccountOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.orm.stripe_payment_intent_reference import StripePaymentIntentReferenceOrm
from eave.core.orm.util.mixins import CoordinatesMixin, GetOneByIdMixin, TimedEventMixin
from eave.core.orm.util.user_defined_column_types import ActivitySourceColumnType, AddressColumnType, RestaurantSourceColumnType
from eave.core.shared.address import Address
from eave.core.shared.enums import ActivitySource, RestaurantSource
from eave.stdlib.typing import NOT_SET

from .base import Base
from .util.constants import PG_UUID_EXPR, OnDeleteOption

# _account_bookings_join_table = Table(
#     "account_bookings",
#     Base.metadata,
#     Column("booking_id", ForeignKey("bookings.id", ondelete=OnDeleteOption.CASCADE)),
#     Column("account_id", ForeignKey(f"{AccountOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE)),
# )

class BookingOrm(Base, GetOneByIdMixin):
    __tablename__ = "bookings"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)

    stripe_payment_intent_reference_id: Mapped[UUID] = mapped_column(ForeignKey(f"{StripePaymentIntentReferenceOrm.__tablename__}.id", ondelete=OnDeleteOption.SET_NULL), index=True)
    stripe_payment_intent_reference: Mapped[UUID] = relationship(lazy="selectin")

    reserver_details_id: Mapped[UUID] = mapped_column(ForeignKey(f"{ReserverDetailsOrm.__tablename__}.id", ondelete=OnDeleteOption.SET_NULL), index=True)
    reserver_details: Mapped[ReserverDetailsOrm] = relationship(lazy="selectin")

    # accounts: Mapped[list[AccountOrm]] = relationship(secondary=_account_bookings_join_table, lazy="selectin")

    activities: Mapped[list["BookingActivityTemplateOrm"]] = relationship(lazy="selectin")
    reservations: Mapped[list["BookingReservationTemplateOrm"]] = relationship(lazy="selectin")

    # def __init__(
    #     self,
    #     *,
    #     stripe_payment_intent_reference_id: UUID,
    # ) -> None:
    #     self.stripe_payment_intent_reference_id = stripe_payment_intent_reference_id,

class BookingActivityTemplateOrm(Base, TimedEventMixin, CoordinatesMixin):
    """Editable template for a booked activity.
    Edits are visible to other accounts part of the same booking, but
    not other bookings created from the same outing. Also does not
    mutate the activity this template cloned its source data from."""

    __tablename__ = "booking_activity_templates"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    booking_id: Mapped[UUID] = mapped_column(ForeignKey(f"{BookingOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE), index=True)
    source_id: Mapped[str] = mapped_column()
    source: Mapped[ActivitySource] = mapped_column(type_=ActivitySourceColumnType())
    """ActivitySource enum value"""
    name: Mapped[str] = mapped_column()
    photo_uri: Mapped[str | None] = mapped_column()
    headcount: Mapped[int] = mapped_column()
    external_booking_link: Mapped[str | None] = mapped_column()
    """HTTP link to site for manual booking (possibly affiliate), if available"""
    address: Mapped[Address] = mapped_column(type_=AddressColumnType())

    # def __init__(
    #     self,
    #     *,
    #     source: ActivitySource,
    #     source_id: str,
    #     name: str,
    #     start_time_utc: datetime,
    #     timezone: ZoneInfo,
    #     photo_uri: str | None,
    #     headcount: int,
    #     external_booking_link: str | None,
    #     address: Address,
    #     lat: float,
    #     lon: float,
    # ) -> None:
    #     self.source = source
    #     self.source_id = source_id
    #     self.name = name
    #     self.start_time_utc = start_time_utc.astimezone(UTC)
    #     self.timezone = timezone
    #     self.photo_uri = photo_uri
    #     self.headcount = headcount
    #     self.external_booking_link = external_booking_link
    #     self.address = address
    #     self.coordinates = GeoPoint(lat=lat, lon=lon).geoalchemy_shape()


class BookingReservationTemplateOrm(Base, TimedEventMixin, CoordinatesMixin):
    """Editable template for a booked reservation.
    Edits are visible to other accounts part of the same booking, but
    not other bookings created from the same outing. Also does not
    mutate the reservation this template cloned its source data from."""

    __tablename__ = "booking_reservation_templates"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    booking_id: Mapped[UUID] = mapped_column(ForeignKey(f"{BookingOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE), index=True)
    source_id: Mapped[str] = mapped_column()
    source: Mapped[RestaurantSource] = mapped_column(type_=RestaurantSourceColumnType())
    """RestaurantSource enum value"""
    name: Mapped[str] = mapped_column()
    photo_uri: Mapped[str | None] = mapped_column()
    headcount: Mapped[int] = mapped_column()
    external_booking_link: Mapped[str | None] = mapped_column()
    """HTTP link to site for manual booking (possibly affiliate), if available"""
    address: Mapped[Address] = mapped_column(type_=AddressColumnType())

    # def __init__(
    #     self,
    #     *,
    #     booking_id: UUID,
    #     source: RestaurantSource,
    #     source_id: str,
    #     name: str,
    #     start_time_utc: datetime,
    #     timezone: ZoneInfo,
    #     photo_uri: str | None,
    #     headcount: int,
    #     external_booking_link: str | None,
    #     address: Address,
    #     lat: float,
    #     lon: float,
    # ) -> None:
    #     self.booking_id = booking_id
    #     self.source = source
    #     self.source_id = source_id
    #     self.name = name
    #     self.start_time_utc = start_time_utc.astimezone(UTC)
    #     self.timezone = timezone
    #     self.photo_uri = photo_uri
    #     self.headcount = headcount
    #     self.external_booking_link = external_booking_link
    #     self.address = address
    #     self.coordinates = GeoPoint(lat=lat, lon=lon).geoalchemy_shape()

    @classmethod
    async def get_one(cls, session: AsyncSession, *, booking_id: UUID, uid: UUID) -> Self:
        return await session.get_one(cls, (booking_id, uid))
