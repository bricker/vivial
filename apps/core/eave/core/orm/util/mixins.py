from datetime import datetime
from enum import StrEnum
from typing import cast
from zoneinfo import ZoneInfo
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, func, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import UserDefinedType

from geoalchemy2 import WKBElement
from geoalchemy2.types import Geography
import shapely.wkb
from shapely.geometry import Point

from eave.core.lib.geo import GeoPoint, SpatialReferenceSystemId
from eave.core.orm.util.user_defined_column_types import ZoneInfoColumnType

class TimedEventMixin:
    start_time_utc: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=True))
    timezone: Mapped[ZoneInfo] = mapped_column(type_=ZoneInfoColumnType())

    @property
    def start_time_local(self) -> datetime:
        return self.start_time_utc.astimezone(self.timezone)

class CoordinatesMixin:
    coordinates: Mapped[WKBElement] = mapped_column(
        type_=Geography(geometry_type="POINT", srid=SpatialReferenceSystemId.LAT_LON)
    )

    def coordinates_to_lat_lon(self) -> tuple[float, float]:
        geometry = cast(Point, shapely.wkb.loads(bytes(self.coordinates.data)))
        return (geometry.x, geometry.y)
