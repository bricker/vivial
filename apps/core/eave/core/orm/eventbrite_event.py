from datetime import datetime
from typing import Self
from uuid import UUID

from geoalchemy2.elements import WKBElement
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.types import Geography
from sqlalchemy import PrimaryKeyConstraint, Select, func, or_, select
from sqlalchemy.dialects.postgresql import INT4RANGE, TSTZRANGE, Range
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.lib.geo import GeoArea, GeoPoint, SpatialReferenceSystemId
from eave.stdlib.typing import NOT_SET

from .base import Base
from .util import PG_UUID_EXPR


class EventbriteEventOrm(Base):
    __tablename__ = "eventbrite_events"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    eventbrite_event_id: Mapped[str] = mapped_column(unique=True)
    title: Mapped[str] = mapped_column()
    time_range: Mapped[Range[datetime]] = mapped_column(TSTZRANGE)
    cost_cents_range: Mapped[Range[int]] = mapped_column(INT4RANGE)
    coordinates: Mapped[WKBElement] = mapped_column(
        type_=Geography(geometry_type="POINT", srid=SpatialReferenceSystemId.LAT_LON)
    )
    vivial_category_id: Mapped[UUID] = mapped_column()
    vivial_format_id: Mapped[UUID] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

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
        min_cost_cents: int | None,
        max_cost_cents: int | None,
        lat: float,
        lon: float,
        vivial_category_id: UUID,
        vivial_format_id: UUID,
    ) -> Self:
        self.title = title
        self.time_range = Range(lower=start_time, upper=end_time, bounds="[)")

        # The int4range range type in postgresql always uses the lower-inclusive bounds ("[)"), so the given "bounds" value here is actually ignored on insert.
        # Because the upper bound is exclusive, but the max_cost_cents value passed in is interpreted as the maximum amount the user is willing to pay (i.e. inclusive),
        # we therefore add 1 (cent) to the upper bound value so that the given max_cost_cents value is inluded in the range.
        # https://www.postgresql.org/docs/current/rangetypes.html#RANGETYPES-DISCRETE
        if max_cost_cents is not None:
            max_cost_cents += 1

        self.cost_cents_range = Range(lower=min_cost_cents, upper=max_cost_cents, bounds="[)")
        self.coordinates = GeoPoint(lat=lat, lon=lon).geoalchemy_shape()
        self.vivial_category_id = vivial_category_id
        self.vivial_format_id = vivial_format_id
        return self

    @classmethod
    def select(
        cls,
        *,
        eventbrite_event_id: str = NOT_SET,
        cost_range_contains: int | None = NOT_SET,
        time_range_contains: datetime = NOT_SET,
        within_areas: list[GeoArea] = NOT_SET,
        vivial_category_ids: list[UUID] = NOT_SET,
    ) -> Select[tuple[Self]]:
        lookup = select(cls)

        if eventbrite_event_id is not NOT_SET:
            lookup = lookup.where(cls.eventbrite_event_id == eventbrite_event_id)

        if vivial_category_ids is not NOT_SET:
            lookup = lookup.where(or_(*[cls.vivial_category_id == vivial_category_id for vivial_category_id in vivial_category_ids]))

        if cost_range_contains is not NOT_SET and cost_range_contains is not None:
            lookup = lookup.where(cls.cost_cents_range.contains(cost_range_contains))

        if time_range_contains is not NOT_SET:
            lookup = lookup.where(cls.time_range.contains(time_range_contains))

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
