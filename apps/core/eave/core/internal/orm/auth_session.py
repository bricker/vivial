from dataclasses import dataclass
import secrets
import typing
import uuid
from datetime import datetime
from typing import Any, Literal, Optional, Self, Tuple
from uuid import UUID
from eave.core.internal.orm.account import AccountOrm

import eave.stdlib.exceptions
import eave.core.internal
import slack_sdk.errors
from sqlalchemy import ForeignKeyConstraint, Index, PrimaryKeyConstraint, Select, func, or_, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from eave.stdlib.core_api.models.account import AnalyticsAccount, AuthenticatedAccount
from eave.stdlib.core_api.models.account import AuthProvider

from eave.stdlib.exceptions import MissingOAuthCredentialsError
from eave.stdlib.logging import LogContext, eaveLogger
from eave.stdlib.typing import JsonObject
from eave.stdlib.util import ensure_uuid_or_none

from .base import Base
from .team import TeamOrm
from .util import UUID_DEFAULT_EXPR, make_team_composite_pk, make_team_fk


class AuthSessionOrm(Base):
    __tablename__ = "auth_sessions"
    __table_args__ = (
        PrimaryKeyConstraint(
            "account_id",
            "id",
        ),
        ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            ondelete="CASCADE",
        ),
        Index(
            None,
            "session_id",
            unique=True,
        ),
        Index(
            None,
            "account_id",
            "session_id",
            unique=True,
        ),
    )

    account_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    session_id: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        account_id: UUID,
    ) -> Self:
        obj = cls(
            account_id=account_id,
            session_id=secrets.token_hex()
        )

        session.add(obj)
        await session.flush()
        return obj

    @dataclass
    class QueryParams:
        account_id: Optional[uuid.UUID] = None
        session_id: Optional[str] = None

        def validate(self) -> None:
            assert self.account_id or self.session_id

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[Tuple[Self]]:
        params.validate()
        lookup = select(cls).limit(1)

        if params.account_id is not None:
            lookup = lookup.where(cls.account_id == params.account_id)

        if params.session_id is not None:
            lookup = lookup.where(cls.session_id == params.session_id)

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup

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

    async def get_account(self, session: AsyncSession) -> AccountOrm:
        account = await AccountOrm.one_or_exception(
            session=session,
            params=AccountOrm.QueryParams(
                id=self.account_id,
            )
        )
        return account