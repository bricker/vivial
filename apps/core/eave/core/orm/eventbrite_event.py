from datetime import UTC, datetime
from typing import Self
from uuid import UUID
from zoneinfo import ZoneInfo

from geoalchemy2.functions import ST_DWithin
from sqlalchemy import PrimaryKeyConstraint, Select, String, or_, select
from sqlalchemy.dialects.postgresql import INT4RANGE, TSTZRANGE, Range
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.lib.geo import GeoArea, GeoPoint
from eave.core.orm.util.mixins import CoordinatesMixin
from eave.core.orm.util.user_defined_column_types import ZoneInfoColumnType
from eave.stdlib.typing import NOT_SET

from .base import Base
from .util.constants import PG_UUID_EXPR

_TIMERANGE_BOUNDS = "[)"
_COST_BOUNDS = "[)"


class EventbriteEventOrm(Base, CoordinatesMixin):
    __tablename__ = "eventbrite_events"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    eventbrite_event_id: Mapped[str] = mapped_column(unique=True)
    title: Mapped[str] = mapped_column()
    time_range_utc: Mapped[Range[datetime]] = mapped_column(TSTZRANGE)
    timezone: Mapped[ZoneInfo] = mapped_column(type_=ZoneInfoColumnType())
    cost_cents_range: Mapped[Range[int]] = mapped_column(INT4RANGE)
    vivial_activity_category_id: Mapped[UUID] = mapped_column()
    vivial_activity_format_id: Mapped[UUID] = mapped_column()

    @classmethod
    def build(cls, *, eventbrite_event_id: str) -> "EventbriteEventOrm":
        obj = EventbriteEventOrm(eventbrite_event_id=eventbrite_event_id)
        return obj

    def update(
        self,
        *,
        title: str,
        start_time: datetime | None,
        end_time: datetime | None,
        timezone: ZoneInfo | None,
        min_cost_cents: int | None,
        max_cost_cents: int | None,
        lat: float,
        lon: float,
        vivial_activity_category_id: UUID,
        vivial_activity_format_id: UUID,
    ) -> Self:
        self.title = title

        if start_time is not None:
            start_time = start_time.astimezone(UTC)

        if end_time is not None:
            end_time = end_time.astimezone(UTC)

        self.time_range_utc = Range(lower=start_time, upper=end_time, bounds=_TIMERANGE_BOUNDS)
        self.timezone = timezone or ZoneInfo("UTC")

        # The int4range range type in postgresql always uses the lower-inclusive bounds ("[)"), so the given "bounds" value here is actually ignored on insert.
        # Because the upper bound is exclusive, but the max_cost_cents value passed in is interpreted as the maximum amount the user is willing to pay (i.e. inclusive),
        # we therefore add 1 (cent) to the upper bound value so that the given max_cost_cents value is inluded in the range.
        # https://www.postgresql.org/docs/current/rangetypes.html#RANGETYPES-DISCRETE
        if max_cost_cents is not None:
            max_cost_cents += 1

        self.cost_cents_range = Range(lower=min_cost_cents, upper=max_cost_cents, bounds=_COST_BOUNDS)
        self.coordinates = GeoPoint(lat=lat, lon=lon).geoalchemy_shape()
        self.vivial_activity_category_id = vivial_activity_category_id
        self.vivial_activity_format_id = vivial_activity_format_id
        return self

    @classmethod
    def select(
        cls,
        *,
        eventbrite_event_id: str = NOT_SET,
        cost_range_contains: int | None = NOT_SET,
        time_range_contains: datetime = NOT_SET,
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

        if cost_range_contains is not NOT_SET and cost_range_contains is not None:
            lookup = lookup.where(cls.cost_cents_range.contains(cost_range_contains))

        if time_range_contains is not NOT_SET:
            lookup = lookup.where(cls.time_range_utc.contains(time_range_contains.astimezone(UTC)))

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

    @property
    def start_time_local(self) -> datetime | None:
        if self.time_range_utc.lower:
            return self.time_range_utc.lower.astimezone(self.timezone)
        else:
            return None

    @property
    def end_time_local(self) -> datetime | None:
        if self.time_range_utc.upper:
            return self.time_range_utc.upper.astimezone(self.timezone)
        else:
            return None

    @property
    def time_range_local(self) -> Range[datetime]:
        return Range(lower=self.start_time_local, upper=self.end_time_local, bounds=_TIMERANGE_BOUNDS)
