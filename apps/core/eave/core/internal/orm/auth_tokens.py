import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4

from sqlalchemy import ForeignKeyConstraint, Index, PrimaryKeyConstraint, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.core_api.models.account import AuthenticatedAccount

from .base import Base
from .util import UUID_DEFAULT_EXPR


class AuthTokensOrm(Base):
    __tablename__ = "auth_tokens"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            ondelete="CASCADE",
        ),
        Index(
            None,
            "account_id",
            "jwi",
            unique=True,
        ),
    )

    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    account_id: Mapped[UUID] = mapped_column()
    jwi: Mapped[UUID] = mapped_column() # This is separate from the `id` so that we can update it for new token pairs.
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
    ) -> Self:
        obj = cls(
            jwi=uuid4(),
        )

        session.add(obj)
        await session.flush()
        return obj

    @dataclass
    class QueryParams:
        jwi: uuid.UUID
        account_id: uuid.UUID

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[tuple[Self]]:
        lookup = select(cls).limit(1)
        lookup = lookup.where(cls.jwi == params.jwi)
        lookup = lookup.where(cls.account_id == params.account_id)

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
