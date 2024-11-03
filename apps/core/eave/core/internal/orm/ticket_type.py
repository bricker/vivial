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
from geoalchemy2.elements import WKBElement
from geoalchemy2.types import Geography
from sqlalchemy import ARRAY, ForeignKeyConstraint, Index, PrimaryKeyConstraint, Select, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import INT4RANGE, TSTZRANGE, Range

from eave.stdlib.util import b64encode

from .base import Base
from .util import PG_UUID_EXPR

class TicketTypeOrm(Base):
    __tablename__ = "ticket_types"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        ForeignKeyConstraint(
            columns=["activity_id"],
            refcolumns=["activities.id"],
            ondelete="CASCADE",
        )
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    activity_id: Mapped[UUID] = mapped_column()
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    base_cost_cents: Mapped[int] = mapped_column()
    service_fee_cents: Mapped[int] = mapped_column()
    tax_percentage: Mapped[float] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())
