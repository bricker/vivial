from dataclasses import dataclass
from enum import IntEnum
import secrets
import uuid
from datetime import datetime
from typing import Optional, Self, Tuple
from uuid import UUID

from sqlalchemy import Index, ScalarResult, Select, SmallInteger, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_composite_pk, make_team_fk


class ClientScope(IntEnum):
    read = 0b0001
    write = 0b0010
    readwrite = 0b0011


class ClientCredentialsOrm(Base):
    __tablename__ = "client_credentials"
    __table_args__ = (
        make_team_composite_pk(table_name="client_credentials"),
        make_team_fk(),
        Index(
            "client_id_client_secret",
            "id",
            "secret",
            unique=True,
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    secret: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    scope: Mapped[ClientScope] = mapped_column(type_=SmallInteger)
    last_used: Mapped[Optional[datetime]] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: UUID,
        description: Optional[str],
        scope: ClientScope,
    ) -> Self:
        obj = cls(
            team_id=team_id,
            description=description,
            secret=secrets.token_hex(64),
            scope=scope,
        )

        session.add(obj)
        await session.flush()
        return obj

    @dataclass
    class QueryParams:
        id: Optional[uuid.UUID] = None
        team_id: Optional[uuid.UUID] = None
        secret: Optional[str] = None
        scope_includes: Optional[ClientScope] = None

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[Tuple[Self]]:
        lookup = select(cls)

        if params.id is not None:
            lookup = lookup.where(cls.id == params.id)

        if params.team_id is not None:
            lookup = lookup.where(cls.team_id == params.team_id)

        if params.secret is not None:
            lookup = lookup.where(cls.secret == params.secret)

        if params.scope_includes is not None:
            lookup = lookup.where((cls.scope & params.scope_includes) > 0)

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup

    @classmethod
    async def query(cls, session: AsyncSession, params: QueryParams) -> ScalarResult[Self]:
        lookup = cls._build_query(params=params)
        result = await session.scalars(lookup)
        return result

    async def touch(self, session: AsyncSession) -> None:
        self.last_used = datetime.utcnow()
