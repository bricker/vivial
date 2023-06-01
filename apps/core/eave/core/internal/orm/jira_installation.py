import uuid
from datetime import datetime
from typing import NotRequired, Optional, Self, Tuple, TypedDict, Unpack
from uuid import UUID

from sqlalchemy import PrimaryKeyConstraint, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from eave.stdlib.core_api.models.jira import JiraInstallation, RegisterJiraInstallationInput

from eave.stdlib.util import ensure_uuid
from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_fk


class JiraInstallationOrm(Base):
    __tablename__ = "jira_installations"
    __table_args__ = (
        make_team_fk(),
        PrimaryKeyConstraint(
            "client_key",
            "id",
        ),
    )

    team_id: Mapped[Optional[UUID]] = mapped_column()
    """team_id has to be optional because on initial integration we don't know which team the app is associated with."""

    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    client_key: Mapped[str] = mapped_column(index=True, unique=True)
    shared_secret: Mapped[str] = mapped_column()
    base_url: Mapped[str] = mapped_column()
    atlassian_actor_account_id: Mapped[Optional[str]] = mapped_column()
    display_url: Mapped[Optional[str]] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    class _selectparams(TypedDict):
        id: NotRequired[uuid.UUID]
        team_id: NotRequired[uuid.UUID]
        client_key: NotRequired[str]

    @classmethod
    def _build_select(cls, **kwargs: Unpack[_selectparams]) -> Select[Tuple[Self]]:
        lookup = select(cls).limit(1)

        if (id := kwargs.get("id")) is not None:
            lookup = lookup.where(cls.id == id)

        if (team_id := kwargs.get("team_id")) is not None:
            lookup = lookup.where(cls.team_id == team_id)

        if (client_key := kwargs.get("client_key")) is not None:
            lookup = lookup.where(cls.client_key == client_key)

        assert lookup.whereclause is not None
        return lookup

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, **kwargs: Unpack[_selectparams]) -> Self:
        lookup = cls._build_select(**kwargs)
        result = (await session.scalars(lookup)).one()
        return result

    @classmethod
    async def one_or_none(cls, session: AsyncSession, **kwargs: Unpack[_selectparams]) -> Self | None:
        lookup = cls._build_select(**kwargs)
        result = await session.scalar(lookup)
        return result

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        input: RegisterJiraInstallationInput,
        team_id: Optional[uuid.UUID | str] = None,
    ) -> Self:
        obj = cls(
            team_id=ensure_uuid(team_id) if team_id else None,
            client_key=input.client_key,
            shared_secret=input.shared_secret,
            atlassian_actor_account_id=input.atlassian_actor_account_id,
            base_url=input.base_url,
            display_url=input.display_url,
            description=input.description,
        )
        session.add(obj)
        await session.flush()
        return obj

    def update(
        self,
        session: AsyncSession,
        input: RegisterJiraInstallationInput,
    ) -> Self:
        """
        Updates the given attributes.
        The `session` parameter is not used, but is requested to encourage the developer to use this method
        in the intended context of a database session.
        """

        # Note: There is of course a more pythonic way to do this, but I have deliberately chosen to do it
        # the "verbose" way to get the benefits of static typechecking.
        # The problem is that there is nothing currently enforcing that the field names on `UpdateForgeInstallationInput`
        # match the fields names on this ORM, so if either one changes, we should at least get an error from the typechecker.
        #
        # The prettier way to do this is something like:
        #
        #     update_dict = input.dict(
        #         exclude_unset=True,
        #         exclude={"forge_app_installation_id"}
        #     )
        #     for key, value in update_dict.items():
        #         setattr(self, key, value)

        fs = input.__fields_set__

        if ("shared_secret" in fs) and input.shared_secret:
            self.shared_secret = input.shared_secret

        if ("base_url" in fs) and input.base_url:
            self.base_url = input.base_url

        if "atlassian_actor_account_id" in fs:
            self.atlassian_actor_account_id = input.atlassian_actor_account_id

        if "display_url" in fs:
            self.display_url = input.display_url

        if "description" in fs:
            self.description = input.description

        return self

    @property
    def api_model(self) -> JiraInstallation:
        return JiraInstallation.from_orm(self)
