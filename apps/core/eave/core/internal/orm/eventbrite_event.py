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
from geoalchemy2.elements import WKBElement
from sqlalchemy import NUMERIC, Index, PrimaryKeyConstraint, Select, func, select
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
    eventbrite_event_id: Mapped[str] = mapped_column()
    title: Mapped[str] = mapped_column()
    time_range: Mapped[Range[datetime]] = mapped_column(TSTZRANGE)
    cost_cents_range: Mapped[Range[int]] = mapped_column(INT4RANGE)
    coordinates: Mapped[WKBElement] = mapped_column(type_=Geography(geometry_type="POINT", srid=4326))
    category_id: Mapped[UUID] = mapped_column()
    subcategory_id: Mapped[UUID] = mapped_column()
    format_id: Mapped[UUID] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        *,
        eventbrite_event_id: str,
        name: str,
        time_range: BoundRange[datetime | None],
        cost_cents_range: BoundRange[int],
        coordinates: GeoCoordinates,
        category_id: UUID,
        subcategory_id: UUID,
    ) -> Self:
        obj = cls(
            eventbrite_event_id=eventbrite_event_id,
            name=name,
            time_range=Range(lower=time_range.lower, upper=time_range.upper, bounds=BoundInclusivity.LOWER_ONLY),
            cost_cents_range=Range(lower=cost_cents_range.lower, upper=cost_cents_range.upper, bounds=BoundInclusivity.UPPER_ONLY),
            coordinates=f"POINT({coordinates.long} {coordinates.lat})", # long,lat is the correct order. See https://postgis.net/documentation/tips/lon-lat-or-lat-lon/
            category_id=category_id,
            subcategory_id=subcategory_id,
        )

        session.add(obj)
        await session.flush()
        return obj
