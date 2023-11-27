import strawberry.federation as sb
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Self, Sequence, Tuple
from uuid import UUID

from sqlalchemy import Index, PrimaryKeyConstraint, ScalarResult, Select
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from strawberry.unset import UNSET

from eave.stdlib.core_api.models.api_documentation_jobs import (
    ApiDocumentationJob,
    LastJobResult,
    ApiDocumentationJobState,
)

from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_fk, make_team_composite_fk


class ApiDocumentationJobOrm(Base):
    __tablename__ = "api_documentation_jobs"
    __table_args__ = (
        PrimaryKeyConstraint(
            "team_id",
            "github_repo_id",
            "id",
            name="pk_team_id_github_repo_id_id",
        ),
        make_team_fk(),
        make_team_composite_fk(fk_column="github_repo_id", foreign_table="github_repos"),
        Index(
            "team_id_github_repo_id_unique_idx",
            "team_id",
            "github_repo_id",
            unique=True,
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    github_repo_id: Mapped[UUID] = mapped_column()
    """foreign key to github_repos.id"""
    state: Mapped[str] = mapped_column()
    last_result: Mapped[str] = mapped_column(server_default=LastJobResult.none)
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @dataclass
    class QueryParams:
        team_id: UUID
        github_repo_id: UUID = UNSET
        ids: list[UUID] = UNSET

        def validate_or_exception(self):
            assert not self.ids == []

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[Tuple[Self]]:
        params.validate_or_exception()
        lookup = select(cls)

        if params.team_id:
            lookup = lookup.where(cls.team_id == params.team_id)

        if params.github_repo_id:
            lookup = lookup.where(cls.github_repo_id == params.github_repo_id)

        if params.ids:
            lookup = lookup.where(cls.id.in_(params.ids))

        assert lookup.whereclause is not None, "Malformed input"
        return lookup

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: UUID,
        github_repo_id: UUID,
        state: ApiDocumentationJobState,
    ) -> Self:
        obj = cls(
            team_id=team_id,
            github_repo_id=github_repo_id,
            state=state,
        )
        session.add(obj)
        await session.flush()
        return obj

    @classmethod
    async def query(
        cls,
        session: AsyncSession,
        params: QueryParams,
    ) -> ScalarResult[Self]:
        stmt = cls._build_query(params=params)
        result = await session.scalars(stmt)
        return result

    def update(
        self, session: AsyncSession, state: ApiDocumentationJobState, last_result: Optional[LastJobResult]
    ) -> None:
        """`session` intentionally unused; it is present as a hint that this function should only be called inside a db session."""
        if last_result is not None:
            self.last_result = last_result
        self.state = state
