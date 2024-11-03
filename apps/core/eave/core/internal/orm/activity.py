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
from geoalchemy2.elements import WKBElement, WKTElement
from geoalchemy2.types import Geography
from sqlalchemy import ARRAY, Index, PrimaryKeyConstraint, Select, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import INT4RANGE, TSTZRANGE, Range

from eave.stdlib.util import b64encode

from .base import Base
from .util import PG_UUID_EXPR

class ActivityOrm(Base):
    __tablename__ = "activities"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    coordinates: Mapped[WKTElement] = mapped_column(type_=Geography(geometry_type="POINT", srid=4326))
    category_id: Mapped[UUID] = mapped_column()
    subcategory_id: Mapped[UUID] = mapped_column()
    duration_minutes: Mapped[int] = mapped_column()
    availability: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    is_bookable: Mapped[bool] = mapped_column()
    booking_url: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())
