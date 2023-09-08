from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID

from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .util import make_team_fk


class GithubRepoOrm(Base):
    __tablename__ = "github_repos"
    __table_args__ = (
        PrimaryKeyConstraint(
            "team_id",
            "external_repo_id",
        ),
        make_team_fk(),
    )

    class State(StrEnum):
        DISABLED = "disabled"
        ENABLED = "enabled"
        PAUSED = "paused"

    team_id: Mapped[UUID] = mapped_column()
    external_repo_id: Mapped[str] = mapped_column(unique=True)
    """github API node_id for this repo"""
    api_documentation_state: Mapped[State] = mapped_column(server_default=State.DISABLED.value)
    """Activation status of the API documentation feature for this repo. options: disabled, enabled, paused"""
    inline_code_documentation_state: Mapped[State] = mapped_column(server_default=State.DISABLED.value)
    """Activation status of the inline code documentation feature for this repo. options: disabled, enabled, paused"""
    architecture_documentation_state: Mapped[State] = mapped_column(server_default=State.DISABLED.value)
    """Activation status of the architecture documentation feature for this repo. options: disabled, enabled, paused"""
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    # @property
    # def api_model(self) -> GithubRepo:
    #     return GithubRepo.from_orm(self)
