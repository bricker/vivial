import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .util import PG_UUID_EXPR


class BookingOrm(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        ForeignKeyConstraint(
            ["reserver_details_id"],
            ["reserver_details.id"],
            ondelete="CASCADE",
            name="reserver_details_booking_fk",
        ),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    reserver_details_id: Mapped[UUID] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    def build(
        cls,
        *,
        reserver_details_id: UUID,
    ) -> Self:
        obj = cls(
            reserver_details_id=reserver_details_id,
        )

        return obj
