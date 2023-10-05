from datetime import datetime
from typing import NotRequired, Optional, Self, Sequence, TypedDict, Unpack, Tuple
from uuid import UUID

from sqlalchemy import PrimaryKeyConstraint, Select
from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

import eave.stdlib.util
from eave.stdlib.core_api.models.github_repos import GithubRepo, GithubRepoUpdateValues, State, Feature

from .base import Base
from .util import make_team_fk, make_team_composite_fk


class GithubRepoOrm(Base):
    __tablename__ = "github_repos"
    __table_args__ = (
        PrimaryKeyConstraint(
            "team_id",
            "external_repo_id",
        ),
        make_team_fk(),
        make_team_composite_fk("github_installation_id", "github_installations"),
    )

    team_id: Mapped[UUID] = mapped_column()
    github_installation_id: Mapped[Optional[UUID]] = mapped_column()
    """Foreign key to the github_installations table id column. May be NULL for backfill data."""
    external_repo_id: Mapped[str] = mapped_column(unique=True)
    """github API node_id for this repo"""
    display_name: Mapped[Optional[str]] = mapped_column()
    """Human-readable reference, for display only"""
    api_documentation_state: Mapped[str] = mapped_column(server_default=State.DISABLED.value)
    """Activation status of the API documentation feature for this repo. options: disabled, enabled, paused"""
    inline_code_documentation_state: Mapped[str] = mapped_column(server_default=State.DISABLED.value)
    """Activation status of the inline code documentation feature for this repo. options: disabled, enabled, paused"""
    architecture_documentation_state: Mapped[str] = mapped_column(server_default=State.DISABLED.value)
    """Activation status of the architecture documentation feature for this repo. options: disabled, enabled, paused"""
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @property
    def api_model(self) -> GithubRepo:
        return GithubRepo.from_orm(self)

    class QueryParams(TypedDict):
        team_id: NotRequired[UUID | str]
        external_repo_id: NotRequired[Optional[str]]
        external_repo_ids: NotRequired[Optional[list[str]]]
        api_documentation_state: NotRequired[Optional[State]]
        inline_code_documentation_state: NotRequired[Optional[State]]
        architecture_documentation_state: NotRequired[Optional[State]]

    @classmethod
    def _build_query(cls, **kwargs: Unpack[QueryParams]) -> Select[Tuple[Self]]:
        lookup = select(cls)

        if team_id := kwargs.get("team_id"):
            lookup = lookup.where(cls.team_id == eave.stdlib.util.ensure_uuid(team_id))

        external_repo_ids = kwargs.get("external_repo_ids")
        external_repo_id = kwargs.get("external_repo_id")

        assert eave.stdlib.util.nand(
            external_repo_ids is not None, external_repo_id is not None
        ), "external_repo_ids and external_repo_id are mutually exclusive inputs"

        if external_repo_ids:
            lookup = lookup.where(cls.external_repo_id.in_(external_repo_ids))

        if external_repo_id:
            lookup = lookup.where(cls.external_repo_id == external_repo_id)

        if api_documentation_state := kwargs.get("api_documentation_state"):
            lookup = lookup.where(cls.api_documentation_state == api_documentation_state.value)

        if inline_code_documentation_state := kwargs.get("inline_code_documentation_state"):
            lookup = lookup.where(cls.inline_code_documentation_state == inline_code_documentation_state.value)

        if architecture_documentation_state := kwargs.get("architecture_documentation_state"):
            lookup = lookup.where(cls.architecture_documentation_state == architecture_documentation_state.value)

        assert lookup.whereclause is not None, "Malformed input"
        return lookup

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: UUID,
        external_repo_id: str,
        github_installation_id: Optional[UUID],
        display_name: Optional[str],
        api_documentation_state: State = State.DISABLED,
        inline_code_documentation_state: State = State.DISABLED,
        architecture_documentation_state: State = State.DISABLED,
    ) -> Self:
        obj = cls(
            team_id=team_id,
            external_repo_id=external_repo_id,
            github_installation_id=github_installation_id,
            display_name=display_name,
            api_documentation_state=api_documentation_state.value,
            inline_code_documentation_state=inline_code_documentation_state.value,
            architecture_documentation_state=architecture_documentation_state.value,
        )
        session.add(obj)
        await session.flush()
        return obj

    @classmethod
    async def query(
        cls,
        session: AsyncSession,
        **kwargs: Unpack[QueryParams],
    ) -> Sequence[Self]:
        """
        Get/list GithubRepos.
        Optionally provide a list of
        `external_repo_ids` to fetch. Providing None for `external_repo_ids` (or empty list)
        will get all repos for the provided `team_id`.
        """
        stmt = cls._build_query(**kwargs)
        result = (await session.scalars(stmt)).all()
        return result

    @classmethod
    async def one_or_exception(cls, team_id: UUID, external_repo_id: str, session: AsyncSession) -> Self:
        stmt = cls._build_query(team_id=team_id, external_repo_id=external_repo_id).limit(1)
        result = (await session.scalars(stmt)).one()
        return result

    @classmethod
    async def one_or_none(cls, team_id: UUID, external_repo_id: str, session: AsyncSession) -> Self | None:
        stmt = cls._build_query(team_id=team_id, external_repo_id=external_repo_id).limit(1)
        result = await session.scalar(stmt)
        return result

    def update(self, input: GithubRepoUpdateValues) -> None:
        if input.api_documentation_state is not None:
            self.api_documentation_state = input.api_documentation_state.value
        if input.architecture_documentation_state is not None:
            self.architecture_documentation_state = input.architecture_documentation_state.value
        if input.inline_code_documentation_state is not None:
            self.inline_code_documentation_state = input.inline_code_documentation_state.value

    @classmethod
    async def delete_by_repo_ids(cls, team_id: UUID, external_repo_ids: list[str], session: AsyncSession) -> None:
        if len(external_repo_ids) < 1:
            # no work to be done (also dont delete ALL entries for team_id)
            return

        stmt = delete(cls).where(cls.team_id == team_id).where(cls.external_repo_id.in_(external_repo_ids))
        await session.execute(stmt)

    @classmethod
    async def all_repos_match_feature_state(
        cls, team_id: UUID, feature: Feature, state: State, session: AsyncSession
    ) -> bool:
        """
        Check if for a given `team_id` all their repos have the specified `state` for a `feature`.

        This query will make use of the composite index for the team_id where clause, which should filter out
        most entries. However, a linear scan will be used for the feature state comparisons. Hopefully it will
        not be too expensive of a query to scan all the repos of a single team.
        """
        stmt = cls._build_query(team_id=team_id)

        # we find all entries for feature status NOT matching the provided one.
        # if there are 0 matches, that means all rows have the same status
        # for `feature` (or there are 0 rows)
        match feature:
            case Feature.INLINE_CODE_DOCUMENTATION:
                stmt = stmt.where(cls.inline_code_documentation_state != state.value)
            case Feature.API_DOCUMENTATION:
                stmt = stmt.where(cls.api_documentation_state != state.value)
            case Feature.ARCHITECTURE_DOCUMENTATION:
                stmt = stmt.where(cls.architecture_documentation_state != state.value)

        result = (await session.scalars(stmt)).all()
        return len(result) == 0
