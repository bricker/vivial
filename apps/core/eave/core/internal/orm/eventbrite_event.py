from decimal import Decimal
from enum import StrEnum
import hashlib
import hmac
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Self
from uuid import UUID

from eave.stdlib.core_api.models.enums import ActivitySource
from eave.stdlib.geo import GeoCoordinates
from eave.stdlib.ranges import BoundInclusivity, BoundRange
from eave.stdlib.typing import NOT_GIVEN, NotGiven
from geoalchemy2.elements import WKBElement, WKTElement
from sqlalchemy import NUMERIC, Index, PrimaryKeyConstraint, ScalarResult, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import INT4RANGE, TSRANGE, TSTZRANGE, Range
from geoalchemy2.types import Geography
from eave.stdlib.util import b64encode

from .base import Base
from .util import PG_UUID_EXPR


class EventbriteEventOrm(Base):
    __tablename__ = "eventbrite_events"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    eventbrite_event_id: Mapped[str] = mapped_column(unique=True)
    title: Mapped[str] = mapped_column()
    time_range: Mapped[Range[datetime]] = mapped_column(TSTZRANGE)
    cost_cents_range: Mapped[Range[int]] = mapped_column(INT4RANGE)
    coordinates: Mapped[WKBElement | WKTElement] = mapped_column(type_=Geography(geometry_type="POINT", srid=4326)) # The union type is necessary because the coordinates are set as a WKTElement, but received as a WKBElement, so the type is different dependending on how it was built.
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
        coordinates: GeoCoordinates,
        subcategory_id: UUID,
        format_id: UUID,
    ) -> Self:
        self.title=title
        self.time_range=Range(lower=start_time, upper=end_time, bounds="[)")

        # The int4range range type in postgresql always uses the lower-inclusive bounds ("[)"), so the given "bounds" value here is actually ignored on insert.
        # Because the upper bound is exclusive, but the max_cost_cents value passed in is interpreted as the maximum amount the user is willing to pay (i.e. inclusive),
        # we therefore add 1 (cent) to the upper bound value so that the given max_cost_cents value is inluded in the range.
        # https://www.postgresql.org/docs/current/rangetypes.html#RANGETYPES-DISCRETE
        if max_cost_cents is not None:
            max_cost_cents += 1
        self.cost_cents_range=Range(lower=min_cost_cents, upper=max_cost_cents, bounds="[)")
        self.coordinates=WKTElement(coordinates.wkt)
        self.subcategory_id=subcategory_id
        self.format_id = format_id
        return self

    @dataclass
    class QueryParams:
        eventbrite_event_id: str | NotGiven = NOT_GIVEN
        cost_range_contains: int | NotGiven = NOT_GIVEN
        time_range_contains: datetime | NotGiven = NOT_GIVEN
        subcategory_id: UUID | NotGiven = NOT_GIVEN
        limit: int | NotGiven = NOT_GIVEN

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[tuple[Self]]:
        lookup = select(cls)

        if not isinstance(params.eventbrite_event_id, NotGiven):
            lookup = lookup.where(cls.eventbrite_event_id == params.eventbrite_event_id)

        if not isinstance(params.subcategory_id, NotGiven):
            lookup = lookup.where(cls.subcategory_id == params.subcategory_id)

        if not isinstance(params.cost_range_contains, NotGiven):
            lookup = lookup.where(cls.cost_cents_range.contains(params.cost_range_contains))

        if not isinstance(params.time_range_contains, NotGiven):
            lookup = lookup.where(cls.time_range.contains(params.time_range_contains))

        if not isinstance(params.limit, NotGiven):
            lookup = lookup.limit(params.limit)

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup

    @classmethod
    async def query(cls, session: AsyncSession, params: QueryParams) -> ScalarResult[Self]:
        lookup = cls._build_query(params=params)
        result = await session.scalars(lookup)
        return result
