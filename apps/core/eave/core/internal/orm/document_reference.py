from dataclasses import dataclass
import strawberry.federation as sb
from datetime import datetime
from typing import Optional, Self
from uuid import UUID

from sqlalchemy import ScalarResult, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.core_api.models.subscriptions import DocumentReference

from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_composite_pk, make_team_fk


class DocumentReferenceOrm(Base):
    __tablename__ = "document_references"
    __table_args__ = (
        make_team_composite_pk(table_name="document_references"),
        make_team_fk(),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    document_id: Mapped[str] = mapped_column()
    document_url: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(cls, session: AsyncSession, team_id: UUID, document_id: str, document_url: str | None) -> Self:
        obj = cls(
            team_id=team_id,
            document_id=document_id,
            document_url=document_url or "",
        )
        session.add(obj)
        await session.flush()
        return obj

    @dataclass
    class QueryParams:
        team_id: UUID
        id: UUID

    @classmethod
    async def query(cls, session: AsyncSession, params: QueryParams) -> ScalarResult[Self]:
        stmt = select(cls).where(cls.team_id == params.team_id).where(cls.id == params.id)
        result = await session.scalars(stmt)
        return result
