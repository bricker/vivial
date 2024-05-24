import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Self, Tuple
from uuid import UUID

from sqlalchemy import Index, ScalarResult, Select, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.collectors.core.datastructures import DatabaseOperation
from eave.stdlib.core_api.models.virtual_event import VirtualEvent
from eave.stdlib.util import titleize

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
        search_query: str | None = None
        view_id: str | None = None

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[tuple[Self]]:
        lookup = select(cls).order_by(cls.readable_name)

        if params.id is not None:
            lookup = lookup.where(cls.id == params.id)

        if params.team_id is not None:
            lookup = lookup.where(cls.team_id == params.team_id)

        if params.readable_name is not None:
            lookup = lookup.where(cls.readable_name == params.readable_name)

        if params.search_query is not None:
            ## trigram
            lookup = lookup.order_by(
                text("similarity(readable_name, :search_query) desc").bindparams(search_query=params.search_query)

            )

        if params.view_id is not None:
            lookup = lookup.where(cls.view_id == params.view_id)

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup

    @property
    def api_model(self) -> VirtualEvent:
        return VirtualEvent.from_orm(self)

    @classmethod
    async def query(cls, session: AsyncSession, params: QueryParams) -> ScalarResult[Self]:
        lookup = cls._build_query(params=params)
        result = await session.scalars(lookup)
        return result


def make_virtual_event_readable_name(*, operation: str, table_name: str) -> str:
    """
    >>> make_virtual_event_readable_name(operation="INSERT", table_name="accounts")
    'Account Created'
    >>> make_virtual_event_readable_name(operation="UPDATE", table_name="github_installations")
    'Github Installation Updated'
    >>> make_virtual_event_readable_name(operation="DELETE", table_name="UserAccounts")
    'User Account Deleted'
    """
    obj_hr = titleize(table_name)
    op_hr = DatabaseOperation(value=operation.upper()).hr_past_tense
    return f"{obj_hr} {op_hr}"
