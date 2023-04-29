from . import UUID_DEFAULT_EXPR, Base, make_team_composite_pk, make_team_fk


from sqlalchemy import Index, func
from sqlalchemy.orm import Mapped, mapped_column


from datetime import datetime
from typing import Optional
from uuid import UUID


# class GithubInstallationOrm(Base):
#     __tablename__ = "github_installations"
#     __table_args__ = (
#         make_team_composite_pk(),
#         make_team_fk(),
#         Index(
#             "eave_team_id_github_install_id",
#             "team_id",
#             "github_install_id",
#             unique=True,
#         ),
#     )

#     team_id: Mapped[UUID] = mapped_column()
#     id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
#     github_install_id: Mapped[str] = mapped_column(unique=True)
#     # TODO: Oauth token storage
#     created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
#     updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())