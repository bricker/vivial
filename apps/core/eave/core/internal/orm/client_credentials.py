import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import IntEnum
from typing import Self
from uuid import UUID

from sqlalchemy import Index, ScalarResult, Select, SmallInteger, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.collectors.core.correlation_context.base import corr_ctx_symmetric_encryption_key

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
    description: Mapped[str | None] = mapped_column()
    scope: Mapped[ClientScope] = mapped_column(type_=SmallInteger)
    last_used: Mapped[datetime | None] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: UUID,
        description: str | None,
        scope: ClientScope,
    ) -> Self:
        obj = cls(
            team_id=team_id,
            description=description,
            secret=f"evc_{secrets.token_hex(64)}", # The prefix helps static code scanners detect secrets
            scope=scope,
        )

        session.add(obj)
        await session.flush()
        return obj

    @dataclass
    class QueryParams:
        id: uuid.UUID | None = None
        team_id: uuid.UUID | None = None
        secret: str | None = None
        scope_includes: ClientScope | None = None

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[tuple[Self]]:
        lookup = select(cls)

        if params.id is not None:
            lookup = lookup.where(cls.id == params.id)

        if params.team_id is not None:
            lookup = lookup.where(cls.team_id == params.team_id)

        if params.secret is not None:
            lookup = lookup.where(cls.secret == params.secret)

        if params.scope_includes is not None:
            lookup = lookup.where(cls.scope.op("&")(params.scope_includes) > 0)

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup

    @classmethod
    async def query(cls, session: AsyncSession, params: QueryParams) -> ScalarResult[Self]:
        lookup = cls._build_query(params=params)
        result = await session.scalars(lookup)
        return result

    def touch(self, session: AsyncSession) -> None:
        # The database column is timezone-naive, so we have to remove the timezone info before saving it to the database.
        self.last_used = datetime.now(UTC).replace(tzinfo=None)

    @property
    def combined(self) -> str:
        # NOTE: This cannot change, because it must match the format of the credentials string in customer's environments.
        return f"{self.id}:{self.secret}"

    @property
    def decryption_key(self) -> bytes:
        return corr_ctx_symmetric_encryption_key(self.combined)
