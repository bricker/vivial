from datetime import datetime
from typing import NotRequired, Optional, Self, Sequence, TypedDict, Unpack, Tuple
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, Select, Index
from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.core_api.models.github_documents import GithubDocument, GithubDocumentValuesInput, Status, DocumentType
from eave.stdlib.util import ensure_uuid_or_none

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
            "id",
            unique=True,
        ),
    )

    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    team_id: Mapped[UUID] = mapped_column()
    external_repo_id: Mapped[str] = mapped_column()
    """Github API node_id for this repo"""
    pull_request_number: Mapped[Optional[int]] = mapped_column(server_default=None)
    """Number of the most recent PR opened for this document"""
    status: Mapped[str] = mapped_column(server_default=Status.PROCESSING.value)
    """Current state of API documentation for this repo. options: processing, under-review, up-to-date"""
    status_updated: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    """Last time the `status` column was updated."""
    file_path: Mapped[Optional[str]] = mapped_column()
    """Relative file path to this document in the given repo."""
    api_name: Mapped[Optional[str]] = mapped_column()
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

        if team_id := ensure_uuid_or_none(kwargs.get("team_id")):
            lookup = lookup.where(cls.team_id == team_id)
        if external_repo_id := kwargs.get("external_repo_id"):
            lookup = lookup.where(cls.external_repo_id == external_repo_id)
        if id := ensure_uuid_or_none(kwargs.get("id")):
            lookup = lookup.where(cls.id == id)
        if type := kwargs.get("type"):
            lookup = lookup.where(cls.type == type.value)

        return lookup

    @classmethod
    async def query(cls, session: AsyncSession, **kwargs: Unpack[QueryParams]) -> Sequence[Self]:
        stmt = cls._build_query(**kwargs)
        results = (await session.scalars(stmt)).all()
        return results

    @classmethod
    async def one_or_exception(cls, team_id: UUID, id: UUID, session: AsyncSession) -> Self:
        stmt = cls._build_query(team_id=team_id, id=id)
        result = (await session.scalars(stmt)).one()
        return result

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: UUID,
        external_repo_id: str,
        type: DocumentType,
        file_path: Optional[str] = None,
        api_name: Optional[str] = None,
        pull_request_number: Optional[int] = None,
        status: Status = Status.PROCESSING,
        status_updated: Optional[datetime] = None,
    ) -> Self:
        obj = cls(
            team_id=team_id,
            external_repo_id=external_repo_id,
            file_path=file_path,
            api_name=api_name,
            type=type.value,
            pull_request_number=pull_request_number,
            status=status.value,
            status_updated=status_updated,
        )
        session.add(obj)
        await session.flush()
        return obj

    def update(self, values: GithubDocumentValuesInput) -> None:
        if pull_request_number := values.pull_request_number:
            self.pull_request_number = pull_request_number
        if status := values.status:
            self.status = status
            self.status_updated = datetime.now()
        if file_path := values.file_path:
            self.file_path = file_path
        if api_name := values.api_name:
            self.api_name = api_name

    @classmethod
    async def delete_by_ids(cls, team_id: UUID, ids: list[UUID], session: AsyncSession) -> None:
        if len(ids) < 1:
            # don't delete all the rows
            return

        stmt = delete(cls).where(cls.team_id == team_id).where(cls.id.in_(ids))
        await session.execute(stmt)

    @classmethod
    async def delete_by_type(cls, team_id: UUID, type: DocumentType, session: AsyncSession) -> None:
        stmt = delete(cls).where(cls.team_id == team_id).where(cls.type == type)
        await session.execute(stmt)
