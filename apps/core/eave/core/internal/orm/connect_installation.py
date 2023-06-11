from urllib.parse import urlparse
import uuid
from datetime import datetime
from typing import NotRequired, Optional, Self, Tuple, TypedDict, Unpack
from uuid import UUID

from sqlalchemy import Index, ScalarResult, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from eave.stdlib.core_api.models.connect import (
    AtlassianProduct,
    ConnectInstallation,
    ConnectInstallationPeek,
    RegisterConnectInstallationInput,
)

from eave.stdlib.util import ensure_uuid
from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_fk


class ConnectInstallationOrm(Base):
    __tablename__ = "connect_installations"
    __table_args__ = (
        make_team_fk(),
        Index(
            None,
            "product",
            "client_key",
            unique=True,
        ),
    )

    team_id: Mapped[Optional[UUID]] = mapped_column()
    """team_id has to be optional because on initial integration we don't know which team the app is associated with."""

    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR, primary_key=True)
    product: Mapped[AtlassianProduct] = mapped_column()
    client_key: Mapped[str] = mapped_column()
    shared_secret: Mapped[str] = mapped_column()
    base_url: Mapped[str] = mapped_column()
    """
    base_url for the product, given by Connect installation. Includes the product context path.
    eg: https://eave-fyi.atlassian.net/wiki
    """
    org_url: Mapped[Optional[str]] = mapped_column(index=True)
    """
    base URL for the Atlassian organization
    eg: https://eave-fyi.atlassian.net
    """
    atlassian_actor_account_id: Mapped[Optional[str]] = mapped_column()
    display_url: Mapped[Optional[str]] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    class QueryParams(TypedDict):
        product: NotRequired[AtlassianProduct]
        id: NotRequired[uuid.UUID]
        team_id: NotRequired[uuid.UUID | str | None]
        client_key: NotRequired[str | None]
        org_url: NotRequired[str]

    @classmethod
    def _build_query(cls, **kwargs: Unpack[QueryParams]) -> Select[Tuple[Self]]:
        lookup = select(cls)

        id = kwargs.get("id")
        team_id = kwargs.get("team_id")
        client_key = kwargs.get("client_key")
        org_url = kwargs.get("org_url")
        assert id or team_id or client_key or org_url, "at least one parameter must be specified"

        if product := kwargs.get("product"):
            lookup = lookup.where(cls.product == product)

        if id:
            lookup = lookup.where(cls.id == id)

        if team_id:
            lookup = lookup.where(cls.team_id == team_id)

        if client_key:
            lookup = lookup.where(cls.client_key == client_key)

        if org_url:
            lookup = lookup.where(cls.org_url == org_url)

        assert lookup.whereclause is not None
        return lookup

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, **kwargs: Unpack[QueryParams]) -> Self:
        lookup = cls._build_query(**kwargs).limit(1)
        result = (await session.scalars(lookup)).one()
        return result

    @classmethod
    async def one_or_none(cls, session: AsyncSession, **kwargs: Unpack[QueryParams]) -> Self | None:
        lookup = cls._build_query(**kwargs).limit(1)
        result = await session.scalar(lookup)
        return result

    @classmethod
    async def query(cls, session: AsyncSession, **kwargs: Unpack[QueryParams]) -> ScalarResult[Self]:
        lookup = cls._build_query(**kwargs)
        results = await session.scalars(lookup)
        return results

    @staticmethod
    def make_org_url(base_url: str) -> str:
        u = urlparse(base_url)
        base = f"{u.scheme}://{u.netloc}"
        return base

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        client_key: str,
        product: AtlassianProduct,
        base_url: str,
        shared_secret: str,
        atlassian_actor_account_id: Optional[str] = None,
        display_url: Optional[str] = None,
        description: Optional[str] = None,
        team_id: Optional[uuid.UUID | str] = None,
    ) -> Self:
        obj = cls(
            team_id=ensure_uuid(team_id) if team_id else None,
            product=product,
            client_key=client_key,
            shared_secret=shared_secret,
            atlassian_actor_account_id=atlassian_actor_account_id,
            base_url=base_url,
            org_url=cls.make_org_url(base_url),
            display_url=display_url,
            description=description,
        )
        session.add(obj)
        await session.flush()
        return obj

    def update(
        self,
        session: AsyncSession,
        input: RegisterConnectInstallationInput,
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
            self.org_url = self.make_org_url(input.base_url)

        if "atlassian_actor_account_id" in fs:
            self.atlassian_actor_account_id = input.atlassian_actor_account_id

        if "display_url" in fs:
            self.display_url = input.display_url

        if "description" in fs:
            self.description = input.description

        return self

    @property
    def api_model(self) -> ConnectInstallation:
        return ConnectInstallation.from_orm(self)

    @property
    def api_model_peek(self) -> ConnectInstallationPeek:
        return ConnectInstallationPeek.from_orm(self)
