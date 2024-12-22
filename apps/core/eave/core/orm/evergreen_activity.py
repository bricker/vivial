from dataclasses import dataclass
from datetime import date
from typing import NamedTuple, Self
from uuid import UUID

from sqlalchemy import ARRAY, DATE, TIMESTAMP, Column, ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint, Select, Table
from sqlalchemy.dialects.postgresql import INT4MULTIRANGE, INT4RANGE, Range
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.operators import op
from sqlalchemy.sql.sqltypes import DATETIME_TIMEZONE, TIME_TIMEZONE

from eave.core.lib.address import Address
from eave.core.orm.image import ImageOrm
from eave.core.orm.util.mixins import CoordinatesMixin, GetOneByIdMixin
from eave.core.orm.util.user_defined_column_types import AddressColumnType
from eave.core.shared.geo import GeoPoint
from eave.stdlib.typing import NOT_SET

from .base import Base
from .util.constants import CASCADE_ALL_DELETE_ORPHAN, PG_UUID_EXPR, OnDeleteOption

_activity_images_join_table = Table(
    "activity_images",
    Base.metadata,
    Column("evergreen_activity_id", ForeignKey("evergreen_activities.id", ondelete=OnDeleteOption.CASCADE.value)),
    Column("image_id", ForeignKey(f"{ImageOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE.value)),
)

# yo dawg
DailyScheduleBlocks = tuple[tuple[int, int], ...]

class WeeklySchedule(NamedTuple):
    monday: DailyScheduleBlocks
    tuesday: DailyScheduleBlocks
    wednesday: DailyScheduleBlocks
    thursday: DailyScheduleBlocks
    friday: DailyScheduleBlocks
    saturday: DailyScheduleBlocks
    sunday: DailyScheduleBlocks


class EvergreenActivityOrm(Base, CoordinatesMixin, GetOneByIdMixin):
    __tablename__ = "evergreen_activities"

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR, primary_key=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    activity_category_id: Mapped[UUID] = mapped_column()
    duration_minutes: Mapped[int] = mapped_column()
    availability: Mapped[list[list[Range[int]]]] = mapped_column(
        type_=ARRAY(
            item_type=INT4MULTIRANGE,
            dimensions=1,
            zero_indexes=True,
        ),
    )
    """
    List of multiranges, where each list element is a day of the week, and each range in the multirange is a range of hours.
    In most cases, there will only be one range per multirange.
    There may be more for places that close temporarily during the day.
    """

    address: Mapped[Address] = mapped_column(type_=AddressColumnType())
    is_bookable: Mapped[bool] = mapped_column()
    booking_url: Mapped[str | None] = mapped_column()

    images: Mapped[list[ImageOrm]] = relationship(secondary=_activity_images_join_table, lazy="selectin")
    ticket_types: Mapped[list["EvergreenActivityTicketTypeOrm"]] = relationship(lazy="selectin", back_populates="evergreen_activity", cascade=CASCADE_ALL_DELETE_ORPHAN)
    weekly_schedules: Mapped[list["WeeklyScheduleOrm"]] = relationship(lazy="selectin", back_populates="evergreen_activity", cascade=CASCADE_ALL_DELETE_ORPHAN)

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        title: str,
        description: str,
        coordinates: GeoPoint,
        activity_category_id: UUID,
        duration_minutes: int,
        availability: list[list[Range[int]]],
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

    @classmethod
    def select(cls, *, business_hours_contains: int = NOT_SET) -> Select[tuple[Self]]:
        query = super().select()

        if business_hours_contains is not NOT_SET:
            query = query.where(cls.availability.op("@>")(business_hours_contains))

        return query

class EvergreenActivityTicketTypeOrm(Base, GetOneByIdMixin):
    __tablename__ = "evergreen_activity_ticket_types"

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR, primary_key=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    base_cost_cents: Mapped[int] = mapped_column()
    service_fee_cents: Mapped[int] = mapped_column()
    tax_percentage: Mapped[float] = mapped_column()

    evergreen_activity_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{EvergreenActivityOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE.value)
    )
    evergreen_activity: Mapped[EvergreenActivityOrm] = relationship(lazy="selectin", back_populates="ticket_types")

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        evergreen_activity: EvergreenActivityOrm,
        title: str,
        description: str,
        base_cost_cents: int,
        service_fee_cents: int,
        tax_percentage: float,
    ) -> None:
        self.evergreen_activity = evergreen_activity
        self.title = title
        self.description = description
        self.base_cost_cents = base_cost_cents
        self.service_fee_cents = service_fee_cents
        self.tax_percentage = tax_percentage

        if session:
            session.add(self)

class WeeklyScheduleOrm(Base, GetOneByIdMixin):
    __tablename__ = "weekly_schedules"

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR, primary_key=True)

    week_of: Mapped[date | None] = mapped_column(type_=DATE)
    """
    Use "week_of" to specify a single week to which this schedule applies.
    If this field is null, then this schedule is considered the default.
    "week_of" can be used to override the default schedule for a single week, eg for holidays.
    The date in this field should be the Monday of that week (i.e., the start of the week).
    """

    monday: Mapped[list[Range]] = mapped_column(type_=INT4MULTIRANGE)
    tuesday: Mapped[list[Range]] = mapped_column(type_=INT4MULTIRANGE)
    wednesday: Mapped[list[Range]] = mapped_column(type_=INT4MULTIRANGE)
    thursday: Mapped[list[Range]] = mapped_column(type_=INT4MULTIRANGE)
    friday: Mapped[list[Range]] = mapped_column(type_=INT4MULTIRANGE)
    saturday: Mapped[list[Range]] = mapped_column(type_=INT4MULTIRANGE)
    sunday: Mapped[list[Range]] = mapped_column(type_=INT4MULTIRANGE)

    evergreen_activity_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{EvergreenActivityOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE.value)
    )
    evergreen_activity: Mapped[EvergreenActivityOrm] = relationship(lazy="selectin", back_populates="weekly_schedules")

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        evergreen_activity: EvergreenActivityOrm,
        monday: list[Range],
        tuesday: list[Range],
        wednesday: list[Range],
        thursday: list[Range],
        friday: list[Range],
        saturday: list[Range],
        sunday: list[Range],
    ) -> None:
        self.evergreen_activity = evergreen_activity
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday
        self.friday = friday
        self.saturday = saturday
        self.sunday = sunday

        if session:
            session.add(self)
