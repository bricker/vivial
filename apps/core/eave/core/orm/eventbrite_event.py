from datetime import UTC, datetime
from typing import Self
from uuid import UUID
from zoneinfo import ZoneInfo

from geoalchemy2.functions import ST_DWithin
from sqlalchemy import PrimaryKeyConstraint, Select, or_, select
from sqlalchemy.dialects.postgresql import TSTZRANGE, Range
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.orm.util.mixins import CoordinatesMixin, GetOneByIdMixin, TimedEventMixin
from eave.core.orm.util.user_defined_column_types import ZoneInfoColumnType
from eave.core.shared.geo import GeoArea, GeoPoint
from eave.stdlib.time import datetime_window
from eave.stdlib.typing import NOT_SET

from .base import Base
from .util.constants import PG_UUID_EXPR


class EventbriteEventOrm(Base, TimedEventMixin, CoordinatesMixin, GetOneByIdMixin):
    __tablename__ = "eventbrite_events"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    eventbrite_event_id: Mapped[str] = mapped_column(unique=True)
    eventbrite_organizer_id: Mapped[str | None] = mapped_column(index=True)
    title: Mapped[str] = mapped_column()
    end_time_utc: Mapped[datetime | None] = mapped_column()
    min_cost_cents: Mapped[int | None] = mapped_column()
    max_cost_cents: Mapped[int | None] = mapped_column()
    vivial_activity_category_id: Mapped[UUID] = mapped_column()
    vivial_activity_format_id: Mapped[UUID] = mapped_column()

    def __init__(self, session: AsyncSession | None, *, eventbrite_event_id: str, eventbrite_organizer_id: str) -> None:
        self.eventbrite_event_id = eventbrite_event_id
        self.eventbrite_organizer_id = eventbrite_organizer_id

        if session:
            session.add(self)

    def update(
        self,
        *,
        title: str,
        start_time: datetime,
        end_time: datetime | None,
        timezone: ZoneInfo,
        min_cost_cents: int,
        max_cost_cents: int,
        lat: float,
        lon: float,
        vivial_activity_category_id: UUID,
        vivial_activity_format_id: UUID,
    ) -> Self:
        self.title = title

        self.start_time_utc = start_time.astimezone(UTC)

        if end_time:
            self.end_time_utc = end_time.astimezone(UTC)
        else:
            self.end_time_utc = None

        self.timezone = timezone

        self.min_cost_cents = min_cost_cents
        self.max_cost_cents = max_cost_cents

        self.coordinates = GeoPoint(lat=lat, lon=lon).geoalchemy_shape()
        self.vivial_activity_category_id = vivial_activity_category_id
        self.vivial_activity_format_id = vivial_activity_format_id
        return self

    @classmethod
    def select(
        cls,
        *,
        eventbrite_event_id: str = NOT_SET,
        up_to_cost_cents: int | None = NOT_SET,
        start_time: datetime = NOT_SET,
        within_areas: list[GeoArea] = NOT_SET,
        vivial_activity_category_ids: list[UUID] = NOT_SET,
    ) -> Select[tuple[Self]]:
        lookup = select(cls)

        if eventbrite_event_id is not NOT_SET:
            lookup = lookup.where(cls.eventbrite_event_id == eventbrite_event_id)

        if vivial_activity_category_ids is not NOT_SET:
            lookup = lookup.where(
                or_(
                    *[
                        cls.vivial_activity_category_id == vivial_activity_category_id
                        for vivial_activity_category_id in vivial_activity_category_ids
                    ]
                )
            )

        if up_to_cost_cents is not NOT_SET and up_to_cost_cents is not None:
            lookup = lookup.where(cls.max_cost_cents <= up_to_cost_cents)

        if start_time is not NOT_SET:
            start_time = start_time.astimezone(UTC)
            # FIXME: This hardcoded minutes window should be passed in
            lower, upper = datetime_window(start_time, minutes=15)
            lookup = lookup.where(cls.start_time_utc.between(lower, upper))

        if within_areas is not NOT_SET:
            lookup = lookup.where(
                or_(
                    *[
                        ST_DWithin(cls.coordinates, area.center.geoalchemy_shape(), area.rad.meters)
                        for area in within_areas
                    ]
                )
            )

        return lookup
