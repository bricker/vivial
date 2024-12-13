from datetime import datetime
from functools import cached_property
from typing import cast
from zoneinfo import ZoneInfo

import shapely.wkb
from geoalchemy2 import WKBElement
from geoalchemy2.types import Geography
from shapely.geometry import Point
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from eave.core.lib.geo import SpatialReferenceSystemId
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

    @cached_property
    def coordinates_lat_lon(self) -> tuple[float, float]:
        geometry = cast(Point, shapely.wkb.loads(bytes(self.coordinates.data)))
        return (geometry.x, geometry.y)
