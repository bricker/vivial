from datetime import datetime
from enum import StrEnum
from typing import Optional, Self
from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_fk


class GithubDocumentsOrm(Base):
    __tablename__ = "github_documents"
    __table_args__ = (
        PrimaryKeyConstraint(
            "team_id",
            "id",
            "external_repo_id",
        ),
        make_team_fk(),
        ForeignKeyConstraint(
            ["external_repo_id"],
            ["github_repos.external_repo_id"],
            ondelete="CASCADE",
        ),
    )

    class Status(StrEnum):
        PROCESSING = "processing"
        PR_OPENED = "pr_opened"
        PR_MERGED = "pr_merged"

    class DocumentType(StrEnum):
        API_DOCUMENT = "api_document"
        ARCHITECTURE_DOCUMENT = "architecture_document"

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    external_repo_id: Mapped[str] = mapped_column()
    """Github API node_id for this repo"""
    pull_request_number: Mapped[int] = mapped_column()
    """Number of the most recent PR opened for this document"""
    status: Mapped[str] = mapped_column(
        server_default=Status.PROCESSING.value
    )  # TODO: should default up-to-date instead??
    """Current state of API documentation for this repo. options: processing, under-review, up-to-date"""
    status_updated: Mapped[Optional[datetime]] = mapped_column(server_default=None)
    file_path: Mapped[str] = mapped_column()
    """Relative file path to this document in the given repo."""
    api_name: Mapped[str] = mapped_column()
    """Name of the API this document is documenting"""
    type: Mapped[str] = mapped_column()
    """Document type. options: api_document, architecture_document"""
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    # @property
    # def api_model(self) -> GithubRepo:
    #     return GithubRepo.from_orm(self)
