import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import PrimaryKeyConstraint, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.core_api.models.account import AuthenticatedAccount

from .base import Base
from .util import UUID_DEFAULT_EXPR

def hash_password(plaintext_password: str) -> str:
    hashed = hashlib.sha256(plaintext_password.encode(), usedforsecurity=True).hexdigest()
    return hashed

class AccountOrm(Base):
    __tablename__ = "accounts"
    __table_args__ = (PrimaryKeyConstraint("id"),)

    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    email: Mapped[str | None] = mapped_column(server_default=None)
    hashed_password: Mapped[str] = mapped_column()
    last_login: Mapped[datetime | None] = mapped_column(server_default=func.current_timestamp(), nullable=True)
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        email: str,
        plaintext_password: str,
    ) -> Self:
        obj = cls(
            email=email,
            hashed_password=hash_password(plaintext_password),
        )

        session.add(obj)
        await session.flush()
        return obj

    @dataclass
    class AuthQueryParams:
        email: str
        plaintext_password: str

    @dataclass
    class QueryParams:
        id: uuid.UUID | None = None
        auth: "AccountOrm.AuthQueryParams | None" = None

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[tuple[Self]]:
        lookup = select(cls).limit(1)

        if params.id is not None:
            lookup = lookup.where(cls.id == params.id)

        if params.auth is not None:
            lookup = lookup.where(cls.email == params.auth.email)
            lookup = lookup.where(cls.hashed_password == hash_password(params.auth.plaintext_password))

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

    @property
    def api_model(self) -> AuthenticatedAccount:
        return AuthenticatedAccount.from_orm(self)
