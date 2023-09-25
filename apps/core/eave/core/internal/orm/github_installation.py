import uuid
from datetime import datetime
from typing import NotRequired, Optional, Self, Tuple, TypedDict, Unpack
from uuid import UUID

from sqlalchemy import Index, Select, func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.core_api.models.github import GithubInstallation, GithubInstallationPeek

from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_composite_pk, make_team_fk


class GithubInstallationOrm(Base):
    __tablename__ = "github_installations"
    __table_args__ = (
        make_team_composite_pk(),
        make_team_fk(),
        Index(
            "eave_team_id_github_install_id",
            "team_id",
            "github_install_id",
            unique=True,
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    github_install_id: Mapped[str] = mapped_column(unique=True, index=True)
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: uuid.UUID,
        github_install_id: str,
    ) -> Self:
        obj = cls(
            team_id=team_id,
            github_install_id=github_install_id,
        )
        session.add(obj)
        await session.flush()
        return obj

    class _selectparams(TypedDict):
        team_id: NotRequired[uuid.UUID]
        github_install_id: NotRequired[str]

    @classmethod
    def _build_select(cls, **kwargs: Unpack[_selectparams]) -> Select[Tuple[Self]]:
        lookup = select(cls).limit(1)

        if (team_id := kwargs.get("team_id")) is not None:
            lookup = lookup.where(cls.team_id == team_id)

        if (github_install_id := kwargs.get("github_install_id")) is not None:
            lookup = lookup.where(cls.github_install_id == github_install_id)

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup

    @classmethod
    async def one_or_none(cls, session: AsyncSession, **kwargs: Unpack[_selectparams]) -> Self | None:
        lookup = cls._build_select(**kwargs)
        result = await session.scalar(lookup)
        return result

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, **kwargs: Unpack[_selectparams]) -> Self:
        lookup = cls._build_select(**kwargs)
        result = (await session.scalars(lookup)).one()
        return result
    
    @classmethod
    async def delete_by_github_install_id(cls, team_id: UUID, github_install_id: str, session: AsyncSession) -> None:
        stmt = delete(cls).where(cls.team_id == team_id).where(cls.github_install_id == github_install_id)
        await session.execute(stmt)

    @property
    def api_model(self) -> GithubInstallation:
        return GithubInstallation.from_orm(self)

    @property
    def api_model_peek(self) -> GithubInstallationPeek:
        return GithubInstallationPeek.from_orm(self)
