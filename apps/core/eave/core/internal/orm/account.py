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
        and re.search("[0-9]", plaintext_password)
        and re.search("[a-zA-Z]", plaintext_password)
        and re.search("[^a-zA-Z0-9]", plaintext_password)
    ):
        return True
    else:
        raise WeakPasswordError()

def hash_password(plaintext_password: str) -> str:
    if plaintext_password is None or len(plaintext_password) == 0:
        raise ValueError("Invalid password")

    hashed = hashlib.sha256(plaintext_password.encode(), usedforsecurity=True).hexdigest()
    return hashed

class AccountOrm(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        Index(
            "unique_email",
            "email",
            unique=True,
        ),
        Index(
            None,
            "email",
            "hashed_password",
        )
    )

    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    email: Mapped[str] = mapped_column()
    SALT!!! hashed_password: Mapped[str] = mapped_column()
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
            assert params.auth.email and params.auth.plaintext_password
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
