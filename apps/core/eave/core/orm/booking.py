from datetime import UTC, datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eave.core.lib.address import Address
from eave.core.orm.account import AccountOrm
from eave.core.orm.account_bookings_join_table import ACCOUNT_BOOKINGS_JOIN_TABLE
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.orm.stripe_payment_intent_reference import StripePaymentIntentReferenceOrm
from eave.core.orm.util.mixins import CoordinatesMixin, GetOneByIdMixin, TimedEventMixin
from eave.core.orm.util.user_defined_column_types import (
    ActivitySourceColumnType,
    AddressFieldsColumnType,
    RestaurantSourceColumnType,
)
from eave.core.shared.enums import ActivitySource, RestaurantSource
from eave.core.shared.geo import GeoPoint

from .base import Base
from .util.constants import PG_UUID_EXPR, OnDeleteOption


class BookingOrm(Base, GetOneByIdMixin):
    __tablename__ = "bookings"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)

    stripe_payment_intent_reference_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{StripePaymentIntentReferenceOrm.__tablename__}.id", ondelete=OnDeleteOption.SET_NULL), index=True
    )
    stripe_payment_intent_reference: Mapped[StripePaymentIntentReferenceOrm | None] = relationship(lazy="selectin")

    reserver_details_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{ReserverDetailsOrm.__tablename__}.id", ondelete=OnDeleteOption.SET_NULL), index=True
    )
    reserver_details: Mapped[ReserverDetailsOrm] = relationship(lazy="selectin")

    accounts: Mapped[list[AccountOrm]] = relationship(
        secondary=ACCOUNT_BOOKINGS_JOIN_TABLE, lazy="selectin", back_populates="bookings"
    )

    activities: Mapped[list["BookingActivityTemplateOrm"]] = relationship(lazy="selectin", back_populates="booking")
    reservations: Mapped[list["BookingReservationTemplateOrm"]] = relationship(
        lazy="selectin", back_populates="booking"
    )

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        accounts: list[AccountOrm],
        reserver_details: ReserverDetailsOrm,
        stripe_payment_intent_reference: StripePaymentIntentReferenceOrm | None = None,
    ) -> None:
        self.reserver_details = reserver_details
        self.stripe_payment_intent_reference = stripe_payment_intent_reference
        self.accounts = accounts

        if session:
            session.add(self)


class BookingActivityTemplateOrm(Base, TimedEventMixin, CoordinatesMixin):
    """Editable template for a booked activity.
    Edits are visible to other accounts part of the same booking, but
    not other bookings created from the same outing. Also does not
    mutate the activity this template cloned its source data from."""

    __tablename__ = "booking_activity_templates"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    source_id: Mapped[str] = mapped_column()
    source: Mapped[ActivitySource] = mapped_column(type_=ActivitySourceColumnType())
    """ActivitySource enum value"""
    name: Mapped[str] = mapped_column()
    photo_uri: Mapped[str | None] = mapped_column()
    headcount: Mapped[int] = mapped_column()
    external_booking_link: Mapped[str | None] = mapped_column()
    """HTTP link to site for manual booking (possibly affiliate), if available"""
    address: Mapped[Address] = mapped_column(type_=AddressFieldsColumnType())

    booking_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{BookingOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE), index=True
    )
    booking: Mapped[BookingOrm] = relationship(lazy="selectin", back_populates="activities")

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        booking: BookingOrm,
        source: ActivitySource,
        source_id: str,
        name: str,
        start_time_utc: datetime,
        timezone: ZoneInfo,
        photo_uri: str | None,
        headcount: int,
        external_booking_link: str | None,
        address: Address,
        coordinates: GeoPoint,
    ) -> None:
        self.booking = booking
        self.source = source
        self.source_id = source_id
        self.name = name
        self.start_time_utc = start_time_utc.astimezone(UTC)
        self.timezone = timezone
        self.photo_uri = photo_uri
        self.headcount = headcount
        self.external_booking_link = external_booking_link
        self.address = address
        self.coordinates = coordinates.geoalchemy_shape()

        if session:
            session.add(self)


class BookingReservationTemplateOrm(Base, TimedEventMixin, CoordinatesMixin):
    """Editable template for a booked reservation.
    Edits are visible to other accounts part of the same booking, but
    not other bookings created from the same outing. Also does not
    mutate the reservation this template cloned its source data from."""

    __tablename__ = "booking_reservation_templates"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    source_id: Mapped[str] = mapped_column()
    source: Mapped[RestaurantSource] = mapped_column(type_=RestaurantSourceColumnType())
    """RestaurantSource enum value"""
    name: Mapped[str] = mapped_column()
    photo_uri: Mapped[str | None] = mapped_column()
    headcount: Mapped[int] = mapped_column()
    external_booking_link: Mapped[str | None] = mapped_column()
    """HTTP link to site for manual booking (possibly affiliate), if available"""
    address: Mapped[Address] = mapped_column(type_=AddressFieldsColumnType())

    booking_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{BookingOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE), index=True
    )
    booking: Mapped[BookingOrm] = relationship(lazy="selectin", back_populates="reservations")

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        booking: BookingOrm,
        source: RestaurantSource,
        source_id: str,
        name: str,
        start_time_utc: datetime,
        timezone: ZoneInfo,
        photo_uri: str | None,
        headcount: int,
        external_booking_link: str | None,
        address: Address,
        coordinates: GeoPoint,
    ) -> None:
        self.booking = booking
        self.source = source
        self.source_id = source_id
        self.name = name
        self.start_time_utc = start_time_utc.astimezone(UTC)
        self.timezone = timezone
        self.photo_uri = photo_uri
        self.headcount = headcount
        self.external_booking_link = external_booking_link
        self.address = address
        self.coordinates = coordinates.geoalchemy_shape()

        if session:
            session.add(self)
