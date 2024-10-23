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

from sqlalchemy import Index, PrimaryKeyConstraint, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.util import b64encode

from .base import Base
from .util import PG_UUID_EXPR

class EventSource(StrEnum):
    eventbrite = "eventbrite"


class EventIndexOrm(Base):
    __tablename__ = "event_index"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        Index(
            None,
            "source",
        ),

        # TODO: Build indices for whatever queries are used for itinerary builder
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)
    source: Mapped[str] = mapped_column()
    source_ref: Mapped[str] = mapped_column()
    title: Mapped[str] = mapped_column()
    start_time: Mapped[datetime] = mapped_column()
    end_time: Mapped[datetime | None] = mapped_column()

    min_cost_cents: Mapped[int] = mapped_column()
    max_cost_cents: Mapped[int] = mapped_column()

    search_area_id: Mapped[str] = mapped_column()
    category_id: Mapped[UUID] = mapped_column()

    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        source: EventSource,
        source_ref: str,
        search_area_id: str,
    ) -> Self:
        obj = cls(
            source=source,
            search_area_id=search_area_id,
        )

        session.add(obj)
        await session.flush()
        return obj

    @dataclass
    class QueryParams:
        id: uuid.UUID | None = None

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[tuple[Self]]:
        lookup = select(cls).limit(1)

        if params.id is not None:
            lookup = lookup.where(cls.id == params.id)

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup

    @classmethod
    async def query(cls, session: AsyncSession, params: QueryParams) -> Self:
        lookup = cls._build_query(params=params)
        result = (await session.scalars(lookup)).one()
        return result

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, params: QueryParams) -> Self:
        lookup = cls._build_query(params=params)
        result = (await session.scalars(lookup)).one()
        return result

    @classmethod
    async def one_or_none(cls, session: AsyncSession, params: QueryParams) -> Self | None:
        lookup = cls._build_query(params=params)
        result = await session.scalar(lookup)
        return result
