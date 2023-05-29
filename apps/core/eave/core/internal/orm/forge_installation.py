import uuid
from datetime import datetime
from typing import NotRequired, Optional, Self, Tuple, TypedDict, Unpack
from uuid import UUID

from sqlalchemy import PrimaryKeyConstraint, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.util import ensure_uuid
from eave.stdlib.core_api.operations.forge import (
    ForgeInstallation,
    UpdateForgeInstallationInput,
    RegisterForgeInstallationInput,
)
from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_fk


class ForgeInstallationOrm(Base):
    __tablename__ = "forge_installations"
    __table_args__ = (
        make_team_fk(),
        PrimaryKeyConstraint(
            "forge_app_installation_id",
            "id",
        ),
    )

    team_id: Mapped[Optional[UUID]] = mapped_column()
    """team_id has to be optional because on initial integration we don't know which team the app is associated with."""

    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    confluence_space_key: Mapped[Optional[str]] = mapped_column()
    forge_app_id: Mapped[str] = mapped_column()
    forge_app_version: Mapped[str] = mapped_column()
    forge_app_installation_id: Mapped[str] = mapped_column(index=True, unique=True)
    forge_app_installer_account_id: Mapped[str] = mapped_column()
    webtrigger_url: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    class _selectparams(TypedDict):
        id: NotRequired[uuid.UUID]
        team_id: NotRequired[uuid.UUID]
        forge_app_id: NotRequired[str]
        forge_app_installation_id: NotRequired[str]

    @classmethod
    def _build_select(cls, **kwargs: Unpack[_selectparams]) -> Select[Tuple[Self]]:
        lookup = select(cls).limit(1)

        if (id := kwargs.get("id")) is not None:
            lookup = lookup.where(cls.id == id)

        if (team_id := kwargs.get("team_id")) is not None:
            lookup = lookup.where(cls.team_id == team_id)

        if (forge_app_id := kwargs.get("forge_app_id")) is not None:
            lookup = lookup.where(cls.forge_app_id == forge_app_id)

        if (forge_app_installation_id := kwargs.get("forge_app_installation_id")) is not None:
            lookup = lookup.where(cls.forge_app_installation_id == forge_app_installation_id)

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
        input: RegisterForgeInstallationInput,
        team_id: Optional[uuid.UUID | str] = None,
    ) -> Self:
        obj = cls(
            team_id=ensure_uuid(team_id) if team_id else None,
            forge_app_id=input.forge_app_id,
            forge_app_version=input.forge_app_version,
            forge_app_installation_id=input.forge_app_installation_id,
            forge_app_installer_account_id=input.forge_app_installer_account_id,
            webtrigger_url=input.webtrigger_url,
            confluence_space_key=input.confluence_space_key,
        )
        session.add(obj)
        await session.flush()
        return obj

    def update(
        self,
        session: AsyncSession,
        input: UpdateForgeInstallationInput,
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
        if ("forge_app_version" in fs) and input.forge_app_version:
            self.forge_app_version = input.forge_app_version

        if ("forge_app_installer_account_id" in fs) and input.forge_app_installer_account_id:
            self.forge_app_installer_account_id = input.forge_app_installer_account_id

        if ("webtrigger_url" in fs) and input.webtrigger_url:
            self.webtrigger_url = input.webtrigger_url

        if "confluence_space_key" in fs:
            self.confluence_space_key = input.confluence_space_key

        return self

    @property
    def api_model(self) -> ForgeInstallation:
        return ForgeInstallation.from_orm(self)
