from datetime import datetime
from uuid import UUID

from geoalchemy2.elements import WKTElement
from geoalchemy2.types import Geography
from sqlalchemy import PrimaryKeyConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .util import PG_UUID_EXPR


class ActivityOrm(Base):
    __tablename__ = "activities"
    __table_args__ = (PrimaryKeyConstraint("id"),)

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
