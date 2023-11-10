from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Self, Sequence, Tuple
from uuid import UUID

from sqlalchemy import Index, ForeignKeyConstraint, Select
from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.core_api.models.api_documentation_jobs import (
    ApiDocumentationJob,
    LastJobResult,
    ApiDocumentationJobState,
)

from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_fk, make_team_composite_pk


class ApiDocumentationJobOrm(Base):
    __tablename__ = "api_documentation_jobs"
    __table_args__ = (
        make_team_composite_pk(),
        make_team_fk(),
        ForeignKeyConstraint(
            ["github_repo_id"],
            ["github_repos.id"],
            ondelete="CASCADE",
            name="github_repos_id_fk",
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    github_repo_id: Mapped[UUID] = mapped_column() # TODO: make part of pk? to make sure no duplicate repo entries
    """foreign key to github_repos.id"""
    state: Mapped[str] = mapped_column()
    last_result: Mapped[str] = mapped_column(server_default=LastJobResult.none)
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @property
    def api_model(self) -> ApiDocumentationJob:
        return ApiDocumentationJob.from_orm(self)

    @dataclass
    class QueryParams:
        team_id: Optional[UUID]
        id: Optional[UUID] = None

        def validate_or_exception(self):
            pass

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[Tuple[Self]]:
        params.validate_or_exception()
        lookup = select(cls)

        if params.team_id:
            lookup = lookup.where(cls.team_id == params.team_id)

        if params.id:
            lookup = lookup.where(cls.id == params.id)

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
    ) -> Sequence[Self]:
        stmt = cls._build_query(params=params)
        result = (await session.scalars(stmt)).all()
        return result

    # @classmethod
    # async def one_or_exception(cls, team_id: UUID, id: UUID, session: AsyncSession) -> Self:
    #     stmt = cls._build_query(cls.QueryParams(team_id=team_id, id=id)).limit(1)
    #     result = (await session.scalars(stmt)).one()
    #     return result

    # @classmethod
    # async def one_or_none(cls, team_id: UUID, id: UUID, session: AsyncSession) -> Self | None:
    #     stmt = cls._build_query(cls.QueryParams(team_id=team_id, id=id)).limit(1)
    #     result = await session.scalar(stmt)
    #     return result

    # def update(self, input: GithubRepoUpdateValues) -> None:
    #     if input.api_documentation_state is not None:
    #         self.api_documentation_state = input.api_documentation_state.value
    #     if input.architecture_documentation_state is not None:
    #         self.architecture_documentation_state = input.architecture_documentation_state.value
    #     if input.inline_code_documentation_state is not None:
    #         self.inline_code_documentation_state = input.inline_code_documentation_state.value
