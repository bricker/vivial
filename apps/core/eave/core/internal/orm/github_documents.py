from datetime import datetime
from enum import StrEnum
from pydoc import Doc
from typing import NotRequired, Optional, Self, Sequence, TypedDict, Unpack, Tuple
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, Index, Select
from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.core_api.models.github_documents import GithubDocument, Status, DocumentType
from eave.stdlib.endpoints import status_payload

from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_fk


class GithubDocumentsOrm(Base):
    __tablename__ = "github_documents"
    __table_args__ = (
        PrimaryKeyConstraint(
            "team_id",
            "external_repo_id",
            "id",
        ),
        make_team_fk(),
        ForeignKeyConstraint(
            ["external_repo_id"],
            ["github_repos.external_repo_id"],
            ondelete="CASCADE",
        ),
        Index(
            None,
            "team_id",
            "external_repo_id",
            unique=True,
        ),
        Index(
            None,
            "id",
            unique=True,
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    external_repo_id: Mapped[str] = mapped_column()
    """Github API node_id for this repo"""
    pull_request_number: Mapped[Optional[int]] = mapped_column(server_default=None)
    """Number of the most recent PR opened for this document"""
    status: Mapped[str] = mapped_column(server_default=Status.PROCESSING.value)
    """Current state of API documentation for this repo. options: processing, under-review, up-to-date"""
    status_updated: Mapped[Optional[datetime]] = mapped_column(server_default=None)
    """Last time the `status` column was updated."""
    file_path: Mapped[str] = mapped_column()
    """Relative file path to this document in the given repo."""
    api_name: Mapped[str] = mapped_column()
    """Name of the API this document is documenting"""
    type: Mapped[str] = mapped_column()
    """Document type. options: api_document, architecture_document"""
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @property
    def api_model(self) -> GithubDocument:
        return GithubDocument.from_orm(self)

    class QueryParams(TypedDict):
        id: NotRequired[UUID | str]
        team_id: NotRequired[UUID | str]
        external_repo_id: NotRequired[str]
        type: NotRequired[DocumentType]

    @classmethod
    def _build_query(cls, **kwargs: Unpack[QueryParams]) -> Select[Tuple[Self]]:
        lookup = select(cls)

        if id := kwargs.get("id"):
            lookup = lookup.where(cls.id == id)
        if team_id := kwargs.get("team_id"):
            lookup = lookup.where(cls.team_id == team_id)
        if external_repo_id := kwargs.get("external_repo_id"):
            lookup = lookup.where(cls.external_repo_id == external_repo_id)
        if type := kwargs.get("type"):
            lookup = lookup.where(cls.type == type)

        return lookup

    @classmethod
    async def query(cls, session: AsyncSession, **kwargs: Unpack[QueryParams]) -> Sequence[Self]:
        stmt = cls._build_query(**kwargs)
        results = (await session.scalars(stmt)).all()
        return results

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: UUID,
        external_repo_id: str,
        file_path: str,
        api_name: str,
        type: DocumentType,
        pull_request_number: Optional[int] = None,
        status: Status = Status.PROCESSING,
        status_updated: Optional[datetime] = None,
    ) -> Self:
        obj = cls(
            team_id=team_id,
            external_repo_id=external_repo_id,
            file_path=file_path,
            api_name=api_name,
            type=type,
            pull_request_number=pull_request_number,
            status=status,
            status_updated=status_updated,
        )
        session.add(obj)
        await session.flush()
        return obj

    @classmethod
    async def delete_by_ids(cls, ids: list[UUID], session: AsyncSession) -> None:
        if len(ids) < 1:
            # dont delete all the rows
            return
        
        stmt = delete(cls).where(cls.id.in_(ids))
        await session.execute(stmt)
