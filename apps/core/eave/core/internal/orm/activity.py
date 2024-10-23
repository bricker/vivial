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
import sqlalchemy.dialects.postgresql

from eave.stdlib.util import b64encode

from .base import Base
from .util import PG_UUID_EXPR

class ActivityOrm(Base):
    __tablename__ = "activities"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
    )

    id: Mapped[UUID] = mapped_column(server_default=PG_UUID_EXPR)

    name: str
    description: str

    # TODO: This needs to be a day-to-hour mapping, eg M 8-22, T 8-22, etc
    hours: Mapped[str] = mapped_column()

    loc_name: Mapped[str] = mapped_column()
    loc_address_1: Mapped[str] = mapped_column()
    loc_address_2: Mapped[str] = mapped_column()
    loc_city: Mapped[str] = mapped_column()
    loc_state: Mapped[str] = mapped_column()
    loc_zip: Mapped[str] = mapped_column()
    loc_lat: Mapped[str] = mapped_column()
    loc_long: Mapped[str] = mapped_column()

    category_id: Mapped[UUID] = mapped_column()

    min_cost_cents: Mapped[int] = mapped_column()
    max_cost_cents: Mapped[int] = mapped_column()

    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        source: ActivitySource,
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
