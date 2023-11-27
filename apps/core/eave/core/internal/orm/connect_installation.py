from dataclasses import dataclass
import strawberry.federation as sb
from urllib.parse import urlparse
import uuid
from datetime import datetime
from typing import Literal, NotRequired, Optional, Self, Tuple, TypedDict, Unpack
from uuid import UUID

from sqlalchemy import Index, ScalarResult, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from strawberry.unset import UNSET
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

    team_id: Mapped[Optional[UUID]] = mapped_column(index=True)
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

    @dataclass
    class QueryParams:
        product: AtlassianProduct = UNSET
        id: uuid.UUID = UNSET
        team_id: uuid.UUID | str = UNSET
        client_key: str = UNSET
        org_url: str = UNSET

        def validate_or_exception(self) -> Literal[True]:
            assert self.product or self.id or self.team_id or self.client_key or self.org_url, "at least one parameter must be specified"
            return True

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[Tuple[Self]]:
        params.validate_or_exception()
        lookup = select(cls)

        if params.product:
            lookup = lookup.where(cls.product == params.product)

        if params.id:
            lookup = lookup.where(cls.id == params.id)

        if params.team_id:
            lookup = lookup.where(cls.team_id == params.team_id)

        if params.client_key:
            lookup = lookup.where(cls.client_key == params.client_key)

        if params.org_url:
            lookup = lookup.where(cls.org_url == params.org_url)

        assert lookup.whereclause is not None
        return lookup

    @classmethod
    async def query(cls, session: AsyncSession, params: QueryParams) -> ScalarResult[Self]:
        lookup = cls._build_query(params=params)
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
