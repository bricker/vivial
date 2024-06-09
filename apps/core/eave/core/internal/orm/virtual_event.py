import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import UUID

from eave.stdlib.typing import JsonObject
from sqlalchemy import JSON, Index, ScalarResult, Select, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.util import titleize
from sqlalchemy.sql.functions import count

from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_composite_pk, make_team_fk


class VirtualEventOrm(Base):
    __tablename__ = "virtual_events"
    __table_args__ = (
        make_team_composite_pk(table_name="virtual_events"),
        make_team_fk(),
        Index(
            "team_id_view_id",
            "team_id",
            "view_id",
            unique=True,
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    readable_name: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column()
    view_id: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: UUID,
        readable_name: str,
        description: str | None,
        view_id: str,
    ) -> Self:
        obj = cls(
            team_id=team_id,
            readable_name=readable_name,
            description=description,
            view_id=view_id,
        )

        session.add(obj)
        await session.flush()
        return obj

    @dataclass
    class QueryParams:
        id: uuid.UUID | None = None
        team_id: uuid.UUID | None = None
        readable_name: str | None = None
        view_id: str | None = None

    @classmethod
    def _build_query[T: Select](cls, builder: T, params: QueryParams) -> T:
        if params.id is not None:
            builder = builder.where(cls.id == params.id)

        if params.team_id is not None:
            builder = builder.where(cls.team_id == params.team_id)

        if params.readable_name is not None:
            builder = builder.where(cls.readable_name == params.readable_name)

        if params.view_id is not None:
            builder = builder.where(cls.view_id == params.view_id)

        assert builder.whereclause is not None, "Invalid parameters"
        return builder

    @classmethod
    async def query(cls, session: AsyncSession, params: QueryParams) -> ScalarResult[Self]:
        builder = select(cls).order_by(cls.readable_name)
        lookup = cls._build_query(builder, params=params)
        result = await session.scalars(lookup)
        return result

    @classmethod
    async def count(cls, session: AsyncSession, params: QueryParams) -> int:
        builder = select(count(cls.id))
        lookup = cls._build_query(builder, params=params)
        result = await session.scalars(lookup)
        return result.one()
