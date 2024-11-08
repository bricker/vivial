from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import UUID

from geoalchemy2.elements import WKBElement
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.types import Geography
from sqlalchemy import PrimaryKeyConstraint, Select, func, or_, select
from sqlalchemy.dialects.postgresql import INT4RANGE, TSTZRANGE, Range
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.lib.geo import GeoPoint, SpatialReferenceSystemId
from eave.core.outing.models.geo_area import SearchRegion
from eave.stdlib.typing import NOT_GIVEN, NotGiven

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
    subcategory_id: Mapped[UUID] = mapped_column()
    format_id: Mapped[UUID] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

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
        subcategory_id: UUID,
        format_id: UUID,
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
        self.subcategory_id = subcategory_id
        self.format_id = format_id
        return self

    @dataclass
    class QueryParams:
        eventbrite_event_id: str | NotGiven = NOT_GIVEN
        cost_range_contains: int | NotGiven = NOT_GIVEN
        time_range_contains: datetime | NotGiven = NOT_GIVEN
        within_areas: list[SearchRegion] | NotGiven = NOT_GIVEN
        subcategory_ids: list[UUID] | NotGiven = NOT_GIVEN

    @classmethod
    def select(cls, params: QueryParams) -> Select[tuple[Self]]:
        lookup = select(cls)

        if not isinstance(params.eventbrite_event_id, NotGiven):
            lookup = lookup.where(cls.eventbrite_event_id == params.eventbrite_event_id)

        if not isinstance(params.subcategory_ids, NotGiven):
            lookup = lookup.where(
                or_(*[cls.subcategory_id == subcategory_id for subcategory_id in params.subcategory_ids])
            )

        if not isinstance(params.cost_range_contains, NotGiven):
            lookup = lookup.where(cls.cost_cents_range.contains(params.cost_range_contains))

        if not isinstance(params.time_range_contains, NotGiven):
            lookup = lookup.where(cls.time_range.contains(params.time_range_contains))

        if not isinstance(params.within_areas, NotGiven):
            lookup = lookup.where(
                or_(
                    *[
                        ST_DWithin(cls.coordinates, area.center.geoalchemy_shape(), area.rad.meters)
                        for area in params.within_areas
                    ]
                )
            )

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup
