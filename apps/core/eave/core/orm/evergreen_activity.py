import math
from datetime import date, datetime
from typing import Self, override
from uuid import UUID

from geoalchemy2.functions import ST_DWithin
from sqlalchemy import (
    DATE,
    Column,
    ForeignKey,
    Select,
    Table,
    exists,
    or_,
)
from sqlalchemy.dialects.postgresql import INT4MULTIRANGE, Range
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eave.core.lib.address import Address
from eave.core.orm.image import ImageOrm
from eave.core.orm.util.mixins import CoordinatesMixin, GetOneByIdMixin
from eave.core.orm.util.user_defined_column_types import AddressColumnType
from eave.core.shared.enums import OutingBudget
from eave.core.shared.geo import GeoArea, GeoPoint
from eave.stdlib.typing import NOT_SET

from .base import Base
from .util.constants import CASCADE_ALL_DELETE_ORPHAN, PG_UUID_EXPR, OnDeleteOption

_activity_images_join_table = Table(
    "activity_images",
    Base.metadata,
    Column("evergreen_activity_id", ForeignKey("evergreen_activities.id", ondelete=OnDeleteOption.CASCADE.value)),
    Column("image_id", ForeignKey(f"{ImageOrm.__tablename__}.id", ondelete=OnDeleteOption.CASCADE.value)),
)


class EvergreenActivityOrm(Base, CoordinatesMixin, GetOneByIdMixin):
    __tablename__ = "evergreen_activities"

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR, primary_key=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    activity_category_id: Mapped[UUID] = mapped_column()
    duration_minutes: Mapped[int] = mapped_column()
    address: Mapped[Address] = mapped_column(type_=AddressColumnType())
    google_place_id: Mapped[str | None] = mapped_column()
    is_bookable: Mapped[bool] = mapped_column()
    booking_url: Mapped[str | None] = mapped_column()
    images: Mapped[list[ImageOrm]] = relationship(secondary=_activity_images_join_table, lazy="selectin")
    ticket_types: Mapped[list["EvergreenActivityTicketTypeOrm"]] = relationship(
        lazy="selectin", back_populates="evergreen_activity", cascade=CASCADE_ALL_DELETE_ORPHAN
    )

    def __init__(
        self,
        session: AsyncSession | None,
        *,
        title: str,
        description: str,
        coordinates: GeoPoint,
        activity_category_id: UUID,
        duration_minutes: int,
        address: Address,
        google_place_id: str | None,
        is_bookable: bool,
        booking_url: str | None,
    ) -> None:
        self.title = title
        self.description = description
        self.coordinates = coordinates.geoalchemy_shape()
        self.activity_category_id = activity_category_id
        self.duration_minutes = duration_minutes
        self.address = address
        self.google_place_id = google_place_id
        self.is_bookable = is_bookable
        self.booking_url = booking_url

        if session:
            session.add(self)

    @override
    @classmethod
    def select(
        cls,
        *,
        within_areas: list[GeoArea] = NOT_SET,
        activity_category_ids: list[UUID] = NOT_SET,
        open_at_local: datetime = NOT_SET,
        budget: OutingBudget = NOT_SET,
        excluded_evergreen_activity_ids: list[UUID] = NOT_SET,
    ) -> Select[tuple[Self]]:
        query = super().select()

        if within_areas is not NOT_SET:
            query = query.where(
                or_(
                    *[
                        ST_DWithin(cls.coordinates, area.center.geoalchemy_shape(), area.rad.meters)
                        for area in within_areas
                    ]
                )
            )

        if activity_category_ids is not NOT_SET:
            query = query.where(cls.activity_category_id.in_(activity_category_ids))

        if open_at_local is not NOT_SET:
            min_of_week = (((open_at_local.weekday() * 24) + open_at_local.hour) * 60) + open_at_local.minute

            query = query.join(WeeklyScheduleOrm, WeeklyScheduleOrm.evergreen_activity_id == cls.id).where(
                WeeklyScheduleOrm.minute_spans_local.op("@>")(min_of_week)
            )

        if budget is not NOT_SET and budget.upper_limit_cents is not None:
            # None means no upper limit, in which case there's no need to add this condition
            query = query.where(
                exists(
                    EvergreenActivityTicketTypeOrm.select(total_cost_cents_lte=budget.upper_limit_cents).where(
                        EvergreenActivityTicketTypeOrm.evergreen_activity_id == EvergreenActivityOrm.id
                    )
                )
            )

        if excluded_evergreen_activity_ids is not NOT_SET and len(excluded_evergreen_activity_ids) > 0:
            query = query.where(cls.id.not_in(excluded_evergreen_activity_ids))

        return query


class EvergreenActivityTicketTypeOrm(Base, GetOneByIdMixin):
    __tablename__ = "evergreen_activity_ticket_types"

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR, primary_key=True)
    title: Mapped[str] = mapped_column()
    max_base_cost_cents: Mapped[int] = mapped_column()
    min_base_cost_cents: Mapped[int] = mapped_column()
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
        max_base_cost_cents: int,
        min_base_cost_cents: int,
        service_fee_cents: int,
        tax_percentage: float,
    ) -> None:
        self.evergreen_activity = evergreen_activity
        self.title = title
        self.max_base_cost_cents = max(0, max_base_cost_cents)
        self.min_base_cost_cents = max(0, min_base_cost_cents)
        self.service_fee_cents = max(0, service_fee_cents)
        self.tax_percentage = max(0, tax_percentage)

        if session:
            session.add(self)

    @override
    @classmethod
    def select(
        cls, *, evergreen_activity_id: UUID = NOT_SET, total_cost_cents_lte: int = NOT_SET
    ) -> Select[tuple[Self]]:
        query = super().select()

        if evergreen_activity_id is not NOT_SET:
            query = query.where(EvergreenActivityTicketTypeOrm.evergreen_activity_id == evergreen_activity_id)

        if total_cost_cents_lte is not NOT_SET:
            query = query.where(
                (EvergreenActivityTicketTypeOrm.max_base_cost_cents + EvergreenActivityTicketTypeOrm.service_fee_cents)
                * (EvergreenActivityTicketTypeOrm.tax_percentage + 1)
                <= total_cost_cents_lte
            )

        return query

    @property
    def total_cost_cents(self) -> int:
        return math.floor((self.max_base_cost_cents + self.service_fee_cents) * (1 + self.tax_percentage))


class WeeklyScheduleOrm(Base, GetOneByIdMixin):
    __tablename__ = "weekly_schedules"

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR, primary_key=True)

    minute_spans_local: Mapped[list[Range[int]]] = mapped_column(type_=INT4MULTIRANGE)
    """
    List of ranges of minute-of-week blocks.
    """

    week_of: Mapped[date | None] = mapped_column(type_=DATE)
    """
    Use "week_of" to specify a single week to which this schedule applies.
    If this field is null, then this schedule is considered the default.
    "week_of" can be used to override the default schedule for a single week, eg for holidays.
    The date in this field should be the Monday of that week (i.e., the start of the week).
    """

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
        minute_spans_local: list[Range[int]],
    ) -> None:
        self.evergreen_activity = evergreen_activity
        self.week_of = week_of
        self.minute_spans_local = minute_spans_local

        if session:
            session.add(self)
