from datetime import date, datetime
from typing import NamedTuple, Self, override
from uuid import UUID

from sqlalchemy import (
    DATE,
    Column,
    ForeignKey,
    Select,
    Table,
    or_,
)
from sqlalchemy.dialects.postgresql import INT4MULTIRANGE, Range
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.operators import in_op
from geoalchemy2.functions import ST_DWithin

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
    def select(cls, *, within_areas: list[GeoArea] = NOT_SET, activity_category_ids: list[UUID] = NOT_SET, open_at_local: datetime = NOT_SET, budget: OutingBudget = NOT_SET) -> Select[tuple[Self]]:
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
            query = query.where(
                cls.activity_category_id.in_(activity_category_ids)
            )

        if open_at_local is not NOT_SET:
            min_of_week = (((open_at_local.weekday() * 24) + open_at_local.hour) * 60) + open_at_local.minute

            query = query.join(
                WeeklyScheduleOrm, WeeklyScheduleOrm.evergreen_activity_id == cls.id
            ).where(WeeklyScheduleOrm.minute_spans_local.op("@>")(min_of_week))

        if budget is not NOT_SET and budget.upper_limit_cents is not None:
            # None means no upper limit, in which case there's no need to add this condition
            query = query.join(
                EvergreenActivityTicketTypeOrm, EvergreenActivityTicketTypeOrm.evergreen_activity_id == cls.id
            ).where(
                (
                    EvergreenActivityTicketTypeOrm.base_cost_cents + EvergreenActivityTicketTypeOrm.service_fee_cents
                ) * (
                    EvergreenActivityTicketTypeOrm.tax_percentage + 1
                ) <= budget.upper_limit_cents
            )

        return query

class EvergreenActivityTicketTypeOrm(Base, GetOneByIdMixin):
    __tablename__ = "evergreen_activity_ticket_types"

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR, primary_key=True)
    title: Mapped[str] = mapped_column()
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
        base_cost_cents: int,
        service_fee_cents: int,
        tax_percentage: float,
    ) -> None:
        self.evergreen_activity = evergreen_activity
        self.title = title
        self.base_cost_cents = base_cost_cents
        self.service_fee_cents = service_fee_cents
        self.tax_percentage = tax_percentage

        if session:
            session.add(self)


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

    # @override
    # @classmethod
    # def select(cls, *, open_at_local: datetime = NOT_SET) -> Select[tuple[Self]]:
    #     query = super().select()

    #     if open_at_local is not NOT_SET:
    #         # FIXME: This doesn't handle `week_of`
    #         min_of_week = (((open_at_local.weekday() * 24) + open_at_local.hour) * 60) + open_at_local.minute
    #         query = query.where(cls.minute_spans_local.op("@>")(min_of_week))

    #     return query
