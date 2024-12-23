from datetime import UTC, datetime
from typing import Self, override
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import ForeignKey, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eave.core.lib.address import Address
from eave.core.orm.account import AccountOrm
from eave.core.orm.account_bookings_join_table import ACCOUNT_BOOKINGS_JOIN_TABLE
from eave.core.orm.outing import OutingOrm
from eave.core.orm.reserver_details import ReserverDetailsOrm
from eave.core.orm.stripe_payment_intent_reference import StripePaymentIntentReferenceOrm
from eave.core.orm.survey import SurveyOrm
from eave.core.orm.util.mixins import CoordinatesMixin, GetOneByIdMixin, TimedEventMixin
from eave.core.orm.util.user_defined_column_types import (
    ActivitySourceColumnType,
    AddressColumnType,
    RestaurantSourceColumnType,
    StrEnumColumnType,
)
from eave.core.shared.enums import ActivitySource, BookingState, RestaurantSource
from eave.core.shared.geo import GeoPoint
from eave.stdlib.typing import NOT_SET

from .base import Base
from .util.constants import CASCADE_ALL_DELETE_ORPHAN, PG_UUID_EXPR, OnDeleteOption


class BookingStateColumnType(StrEnumColumnType[BookingState]):
    cache_ok = True

    @override
    def enum_member(self, value: str) -> BookingState:
        return BookingState[value]


class BookingOrm(Base, GetOneByIdMixin):
    __tablename__ = "bookings"

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR, primary_key=True)

    state: Mapped[BookingState] = mapped_column(
        type_=BookingStateColumnType(), server_default=BookingState.INITIATED.value
    )

    stripe_payment_intent_reference_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{StripePaymentIntentReferenceOrm.__tablename__}.id", ondelete=OnDeleteOption.SET_NULL.value),
        index=True,
    )
    stripe_payment_intent_reference: Mapped[StripePaymentIntentReferenceOrm | None] = relationship(lazy="selectin")

    # This is nullable because if the Reserver Details is deleted, we still want to keep this Booking, so we set this field to Null.
    reserver_details_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{ReserverDetailsOrm.__tablename__}.id", ondelete=OnDeleteOption.SET_NULL.value), index=True
    )
    reserver_details: Mapped[ReserverDetailsOrm | None] = relationship(lazy="selectin")

    outing_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(f"{OutingOrm.__tablename__}.id", ondelete=OnDeleteOption.SET_NULL.value), index=True
    )
    outing: Mapped[OutingOrm | None] = relationship(lazy="selectin")

    accounts: Mapped[list[AccountOrm]] = relationship(
        secondary=ACCOUNT_BOOKINGS_JOIN_TABLE, lazy="selectin", back_populates="bookings"
    )

    activities: Mapped[list["BookingActivityTemplateOrm"]] = relationship(
        lazy="selectin", back_populates="booking", cascade=CASCADE_ALL_DELETE_ORPHAN
    )
    reservations: Mapped[list["BookingReservationTemplateOrm"]] = relationship(
        lazy="selectin", back_populates="booking", cascade=CASCADE_ALL_DELETE_ORPHAN
    )

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        accounts: list[AccountOrm],
        reserver_details: ReserverDetailsOrm | None,
        outing: OutingOrm,
        state: BookingState = BookingState.INITIATED,
        stripe_payment_intent_reference: StripePaymentIntentReferenceOrm | None = None,
    ) -> None:
        self.reserver_details = reserver_details
        self.outing = outing
        self.stripe_payment_intent_reference = stripe_payment_intent_reference
        self.accounts = accounts
        self.state = state

        if session:
            session.add(self)

    @override
    @classmethod
    def select(cls, *, account_id: UUID = NOT_SET, uid: UUID = NOT_SET) -> Select[tuple[Self]]:
        query = super().select()

        if uid is not NOT_SET:
            query = query.where(BookingOrm.id == uid).limit(1)

        if account_id is not NOT_SET:
            query = query.join(BookingOrm.accounts).where(AccountOrm.id == account_id)

        return query

    @property
    def timezone(self) -> ZoneInfo:
        if len(self.activities) > 0:
            return self.activities[0].timezone
        elif len(self.reservations) > 0:
            return self.reservations[0].timezone
        else:
            raise ValueError("Invalid Booking: no activities or reservations")

    @property
    def start_time_utc(self) -> datetime:
        candidates: list[datetime] = []
        candidates.extend(a.start_time_utc for a in self.activities)
        candidates.extend(r.start_time_utc for r in self.reservations)

        if len(candidates) == 0:
            raise ValueError("Invalid Booking: no activities or reservations")

        return min(candidates)

    @property
    def start_time_local(self) -> datetime:
        candidates: list[datetime] = []
        candidates.extend(a.start_time_local for a in self.activities)
        candidates.extend(r.start_time_local for r in self.reservations)

        if len(candidates) == 0:
            raise ValueError("Invalid Booking: no activities or reservations")

        return min(candidates)

    @property
    def headcount(self) -> int:
        candidates: list[int] = []
        candidates.extend(a.headcount for a in self.activities)
        candidates.extend(r.headcount for r in self.reservations)

        if len(candidates) == 0:
            raise ValueError("Invalid Booking: no activities or reservations")

        return max(candidates)

    @property
    def survey(self) -> SurveyOrm | None:
        return self.outing.survey if self.outing else None


class BookingActivityTemplateOrm(Base, TimedEventMixin, CoordinatesMixin):
    """Editable template for a booked activity.
    Edits are visible to other accounts part of the same booking, but
    not other bookings created from the same outing. Also does not
    mutate the activity this template cloned its source data from."""

    __tablename__ = "booking_activity_templates"

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR, primary_key=True)
    source_id: Mapped[str] = mapped_column()
    source: Mapped[ActivitySource] = mapped_column(type_=ActivitySourceColumnType())
    """ActivitySource enum value"""
    name: Mapped[str] = mapped_column()
    photo_uri: Mapped[str | None] = mapped_column()
    headcount: Mapped[int] = mapped_column()
    external_booking_link: Mapped[str | None] = mapped_column()
    """HTTP link to site for manual booking (possibly affiliate), if available"""
    address: Mapped[Address] = mapped_column(type_=AddressColumnType())

    booking_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{BookingOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE.value), index=True
    )
    booking: Mapped[BookingOrm] = relationship(
        lazy="selectin",
        back_populates="activities",
    )

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

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR, primary_key=True)
    source_id: Mapped[str] = mapped_column()
    source: Mapped[RestaurantSource] = mapped_column(type_=RestaurantSourceColumnType())
    """RestaurantSource enum value"""
    name: Mapped[str] = mapped_column()
    photo_uri: Mapped[str | None] = mapped_column()
    headcount: Mapped[int] = mapped_column()
    external_booking_link: Mapped[str | None] = mapped_column()
    """HTTP link to site for manual booking (possibly affiliate), if available"""
    address: Mapped[Address] = mapped_column(type_=AddressColumnType())

    booking_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{BookingOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE.value), index=True
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
