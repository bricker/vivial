from datetime import date, datetime
from typing import NamedTuple, Self, override
from uuid import UUID

from sqlalchemy import (
    DATE,
    Column,
    ForeignKey,
    Select,
    Table,
)
from sqlalchemy.dialects.postgresql import INT4MULTIRANGE, Range
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    address: Mapped[Address] = mapped_column(type_=AddressColumnType())
    is_bookable: Mapped[bool] = mapped_column()
    booking_url: Mapped[str | None] = mapped_column()

    images: Mapped[list[ImageOrm]] = relationship(secondary=_activity_images_join_table, lazy="selectin")
    ticket_types: Mapped[list["EvergreenActivityTicketTypeOrm"]] = relationship(
        lazy="selectin", back_populates="evergreen_activity", cascade=CASCADE_ALL_DELETE_ORPHAN
    )
    # weekly_schedules: Mapped[list["WeeklyScheduleOrm"]] = relationship(
    #     lazy="selectin", back_populates="evergreen_activity", cascade=CASCADE_ALL_DELETE_ORPHAN
    # )

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        title: str,
        description: str,
        coordinates: GeoPoint,
        activity_category_id: UUID,
        duration_minutes: int,
        # weekly_schedules: list["WeeklyScheduleOrm"],
        address: Address,
        is_bookable: bool,
        booking_url: str | None,
    ) -> None:
        self.title = title
        self.description = description
        self.coordinates = coordinates.geoalchemy_shape()
        self.activity_category_id = activity_category_id
        self.duration_minutes = duration_minutes
        # self.weekly_schedules = weekly_schedules
        self.address = address
        self.is_bookable = is_bookable
        self.booking_url = booking_url

        if session:
            session.add(self)

    # def schedule_for_week(self, *, start_of_week: datetime) -> "WeeklyScheduleOrm | None":
    #     """
    #     Find a schedule that starts on the given date.
    #     If none exists, then find a schedule without a date (default schedule).
    #     """
    #     return next((s for s in self.weekly_schedules if s.week_of == start_of_week), None) or next(
    #         (s for s in self.weekly_schedules if s.week_of is None), None
    #     )


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

    monday: Mapped[list[Range[int]]] = mapped_column(type_=INT4MULTIRANGE)
    tuesday: Mapped[list[Range[int]]] = mapped_column(type_=INT4MULTIRANGE)
    wednesday: Mapped[list[Range[int]]] = mapped_column(type_=INT4MULTIRANGE)
    thursday: Mapped[list[Range[int]]] = mapped_column(type_=INT4MULTIRANGE)
    friday: Mapped[list[Range[int]]] = mapped_column(type_=INT4MULTIRANGE)
    saturday: Mapped[list[Range[int]]] = mapped_column(type_=INT4MULTIRANGE)
    sunday: Mapped[list[Range[int]]] = mapped_column(type_=INT4MULTIRANGE)

    evergreen_activity_id: Mapped[UUID] = mapped_column(
        ForeignKey(f"{EvergreenActivityOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE.value)
    )
    evergreen_activity: Mapped[EvergreenActivityOrm] = relationship(lazy="selectin")

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        evergreen_activity: EvergreenActivityOrm,
        week_of: datetime | None,
        monday: list[Range[int]],
        tuesday: list[Range[int]],
        wednesday: list[Range[int]],
        thursday: list[Range[int]],
        friday: list[Range[int]],
        saturday: list[Range[int]],
        sunday: list[Range[int]],
    ) -> None:
        self.evergreen_activity = evergreen_activity
        self.week_of = week_of
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday
        self.friday = friday
        self.saturday = saturday
        self.sunday = sunday

        if session:
            session.add(self)

    @override
    @classmethod
    def select(cls, *, open_at: datetime = NOT_SET) -> Select[tuple[Self]]:
        query = super().select()

        if open_at is not NOT_SET:
            match open_at.weekday():
                case 0:  # Monday
                    query = query.where(cls.monday.op("<@")(open_at.hour))
                case 1:  # Tuesday
                    query = query.where(cls.tuesday.op("<@")(open_at.hour))
                case 2:  # Wednesday
                    query = query.where(cls.wednesday.op("<@")(open_at.hour))
                case 3:  # Thursday
                    query = query.where(cls.thursday.op("<@")(open_at.hour))
                case 4:  # Friday
                    query = query.where(cls.friday.op("<@")(open_at.hour))
                case 5:  # Saturday
                    query = query.where(cls.saturday.op("<@")(open_at.hour))
                case 6:  # Sunday
                    query = query.where(cls.sunday.op("<@")(open_at.hour))
                case _:
                    raise ValueError("invalid case")

        return query
