import hashlib
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Self
from uuid import UUID

from sqlalchemy import Index, PrimaryKeyConstraint, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.core_api.models.account import AuthenticatedAccount

from .base import Base
from .util import UUID_DEFAULT_EXPR

class WeakPasswordError(Exception):
    pass

def validate_password_or_exception(plaintext_password: str) -> Literal[True]:
    if (
        len(plaintext_password) >= 8
        and len(plaintext_password) < 256 # This is just to keep memory usage reasonable while hashing
        and re.search("[0-9]", plaintext_password)
        and re.search("[a-zA-Z]", plaintext_password)
        and re.search("[^a-zA-Z0-9]", plaintext_password)
    ):
        return True
    else:
        raise WeakPasswordError()

class AccountOrm(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
    )

    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    email: Mapped[str] = mapped_column(unique=True)
    password_key_salt: Mapped[str] = mapped_column()
    password_key: Mapped[str] = mapped_column()
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
    class QueryParams:
        id: uuid.UUID | None = None
        email: str | None = None

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[tuple[Self]]:
        lookup = select(cls).limit(1)

        if params.id is not None:
            lookup = lookup.where(cls.id == params.id)

        if params.email is not None:
            lookup = lookup.where(cls.email == params.email)

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

    def validate_password_or_exception(self, plaintext_password: str) -> Literal[True]:
        pass

    def derive_password_key(self, plaintext_password: str) -> str:
        if not plaintext_password:
            raise ValueError("Invalid password")

        hashed = hashlib.scrypt(plaintext_password.encode(), salt=x)
        return hashed
