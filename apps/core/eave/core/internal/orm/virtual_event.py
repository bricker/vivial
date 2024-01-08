from dataclasses import dataclass
import uuid
from datetime import datetime
from typing import Optional, Self, Tuple
from uuid import UUID

from sqlalchemy import ScalarResult, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.monitoring.datastructures import DatabaseChangeOperation
from eave.stdlib.util import titleize

from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_composite_pk, make_team_fk


class VirtualEventOrm(Base):
    __tablename__ = "virtual_events"
    __table_args__ = (
        make_team_composite_pk(table_name="virtual_events"),
        make_team_fk(),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    name: Mapped[str] = mapped_column(index=True)
    description: Mapped[Optional[str]] = mapped_column()
    view_name: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: UUID,
        name: str,
        description: Optional[str],
        view_name: str,
    ) -> Self:
        obj = cls(
            team_id=team_id,
            name=name,
            description=description,
            view_name=view_name,
        )

        session.add(obj)
        await session.flush()
        return obj

    @dataclass
    class QueryParams:
        id: Optional[uuid.UUID] = None
        team_id: Optional[uuid.UUID] = None
        name: Optional[str] = None
        view_name: Optional[str] = None

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[Tuple[Self]]:
        lookup = select(cls)

        if params.id is not None:
            lookup = lookup.where(cls.id == params.id)

        if params.team_id is not None:
            lookup = lookup.where(cls.team_id == params.team_id)

        if params.name is not None:
            lookup = lookup.where(cls.name == params.name)

        if params.view_name is not None:
            lookup = lookup.where(cls.view_name == params.view_name)

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup

    @classmethod
    async def query(cls, session: AsyncSession, params: QueryParams) -> ScalarResult[Self]:
        lookup = cls._build_query(params=params)
        result = await session.scalars(lookup)
        return result


def make_virtual_event_name(*, operation: str, table_name: str) -> str:
    """
    >>> make_virtual_event_name(operation="INSERT", table_name="accounts")
    'Account Created'
    >>> make_virtual_event_name(operation="UPDATE", table_name="github_installations")
    'Github Installation Updated'
    >>> make_virtual_event_name(operation="DELETE", table_name="UserAccounts")
    'User Account Deleted'
    """
    op_hr = DatabaseChangeOperation(value=operation.upper()).hr_past_tense
    obj_hr = titleize(table_name)
    return f"{obj_hr} {op_hr}"
