from datetime import datetime
from typing import Self, cast
from uuid import UUID
from zoneinfo import ZoneInfo

import geoalchemy2
from geoalchemy2 import WKBElement
from geoalchemy2.types import Geography
from shapely.geometry import Point
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.lib.geo import SpatialReferenceSystemId
from eave.core.orm.util.user_defined_column_types import ZoneInfoColumnType
from eave.core.shared.geo import GeoPoint


class TimedEventMixin:
    start_time_utc: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=True), index=True)
    timezone: Mapped[ZoneInfo] = mapped_column(type_=ZoneInfoColumnType())

    @property
    def start_time_local(self) -> datetime:
        return self.start_time_utc.astimezone(self.timezone)


class CoordinatesMixin:
    coordinates: Mapped[WKBElement] = mapped_column(
        type_=Geography(geometry_type="POINT", srid=SpatialReferenceSystemId.LAT_LON)
    )

    def coordinates_to_geopoint(self) -> GeoPoint:
        geometry = cast(Point, geoalchemy2.shape.to_shape(self.coordinates))
        # Note that the coordinates are stored as (lon,lat) in the database (on purpose, see here: https://postgis.net/documentation/tips/lon-lat-or-lat-lon/)
        # So when they're loaded into a WKB, x is longitude and y is latitude.
        return GeoPoint(lat=geometry.y, lon=geometry.x)


class GetOneByIdMixin:
    @classmethod
    async def get_one(cls, session: AsyncSession, uid: UUID) -> Self:
        return await session.get_one(cls, uid)
