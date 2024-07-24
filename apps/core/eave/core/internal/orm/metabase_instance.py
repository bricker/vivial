import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import Self
from uuid import UUID

from sqlalchemy import Select, String, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.config import SHARED_CONFIG

from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_composite_pk, make_team_fk


class MetabaseInstanceState(IntEnum):
    INIT = 0
    READY = 1


class MetabaseInstanceOrm(Base):
    __tablename__ = "metabase_instances"
    __table_args__ = (
        make_team_composite_pk(table_name="metabase_instances"),
        make_team_fk(),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    state: Mapped[int] = mapped_column(server_default=text(f"{MetabaseInstanceState.READY}"))
    jwt_signing_key: Mapped[str] = mapped_column()
    instance_id: Mapped[str] = mapped_column(
        unique=True, type_=String(length=8)
    )  # The length restraint is important because this value is used for GCP resources, some of which have a maximum length.
    default_dashboard_id: Mapped[str | None] = mapped_column(nullable=True)
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[datetime | None] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: uuid.UUID | None,
        state: MetabaseInstanceState,
    ) -> Self:
        obj = cls(
            team_id=team_id,
            state=state,
            jwt_signing_key=secrets.token_hex(64),
            instance_id=secrets.token_hex(4),
        )
        session.add(obj)
        await session.flush()
        return obj

    @dataclass
    class QueryParams:
        team_id: uuid.UUID | None = None
        id: uuid.UUID | None = None

        def validate_or_exception(self) -> None:
            assert self.team_id or self.id, "At least one query parameter must be given"

    @classmethod
    def _build_select(cls, params: QueryParams) -> Select[tuple[Self]]:
        params.validate_or_exception()

        lookup = select(cls)

        if params.team_id:
            lookup = lookup.where(cls.team_id == params.team_id)

        if params.id:
            lookup = lookup.where(cls.id == params.id)

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup

    @classmethod
    async def query(cls, session: AsyncSession, params: QueryParams) -> Self | None:
        lookup = cls._build_select(params=params).limit(1)
        result = await session.scalar(lookup)
        return result

    @classmethod
    async def one_or_none(cls, session: AsyncSession, team_id: UUID) -> Self | None:
        lookup = cls._build_select(params=cls.QueryParams(team_id=team_id)).limit(1)
        result = await session.scalar(lookup)
        return result

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, team_id: UUID) -> Self:
        lookup = cls._build_select(params=cls.QueryParams(team_id=team_id)).limit(1)
        result = (await session.scalars(lookup)).one()
        return result

    @property
    def internal_base_url(self) -> str:
        return f"http://mb-{self.instance_id}.{SHARED_CONFIG.eave_embed_netloc_internal}"

    @property
    def ready(self) -> bool:
        return self.state == MetabaseInstanceState.READY
