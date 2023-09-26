from datetime import datetime
from typing import NotRequired, Optional, Self, Tuple, TypedDict, Unpack
from typing_extensions import override
from uuid import UUID
import uuid

from sqlalchemy import ForeignKeyConstraint, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from eave.core.internal.document_client import DocumentClient, DocumentMetadata
from eave.core.internal.orm.connect_installation import ConnectInstallationOrm
from eave.stdlib.confluence_api.operations import (
    CreateContentRequest,
    DeleteContentRequest,
    GetAvailableSpacesRequest,
    SearchContentRequest,
    UpdateContentRequest,
)
from eave.stdlib.confluence_api.models import ConfluenceSearchParamsInput, DeleteContentInput, UpdateContentInput
from eave.stdlib.core_api.models.connect import AtlassianProduct
from eave.stdlib.core_api.models.documents import DocumentInput, DocumentSearchResult

from eave.stdlib.core_api.models.team import ConfluenceDestination, ConfluenceDestinationInput
from eave.core.internal.config import app_config
from eave.stdlib.logging import LogContext
from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_composite_pk, make_team_fk
from .. import database


class ConfluenceDestinationOrm(Base):
    __tablename__ = "confluence_destinations"
    __table_args__ = (
        make_team_composite_pk(),
        make_team_fk(),
        ForeignKeyConstraint(["connect_installation_id"], ["connect_installations.id"], ondelete="CASCADE"),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    connect_installation_id: Mapped[uuid.UUID] = mapped_column()
    space_key: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @property
    def api_model(self) -> ConfluenceDestination:
        return ConfluenceDestination.from_orm(self)

    class InsertParams(TypedDict):
        team_id: UUID
        connect_installation_id: UUID
        space_key: str

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs: Unpack[InsertParams]) -> Self:
        obj = cls(
            team_id=kwargs["team_id"],
            connect_installation_id=kwargs["connect_installation_id"],
            space_key=kwargs["space_key"],
        )
        session.add(obj)
        await session.flush()
        return obj

    @classmethod
    async def upsert(cls, session: AsyncSession, **kwargs: Unpack[InsertParams]) -> Self:
        existing = await cls.one_or_none(
            session=session,
            connect_installation_id=kwargs["connect_installation_id"],
        )
        if existing:
            existing.update(space_key=kwargs["space_key"])
            await session.flush()
            return existing
        else:
            new = await cls.create(session=session, **kwargs)
            return new

    class UpdateParams(TypedDict):
        space_key: str

    def update(self, **kwargs: Unpack[UpdateParams]) -> Self:
        self.space_key = kwargs["space_key"]
        return self

    class QueryParams(TypedDict):
        id: NotRequired[UUID]
        team_id: NotRequired[UUID]
        connect_installation_id: NotRequired[UUID]

    @classmethod
    def query(cls, **kwargs: Unpack[QueryParams]) -> Select[Tuple[Self]]:
        id = kwargs.get("id")
        team_id = kwargs.get("team_id")
        connect_installation_id = kwargs.get("connect_installation_id")

        lookup = select(cls)

        if id:
            lookup = lookup.where(cls.id == id)

        if team_id:
            lookup = lookup.where(cls.team_id == team_id)

        if connect_installation_id:
            lookup = lookup.where(cls.connect_installation_id == connect_installation_id)

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, **kwargs: Unpack[QueryParams]) -> Self:
        lookup = cls.query(**kwargs).limit(1)
        result = (await session.scalars(lookup)).one()
        return result

    @classmethod
    async def one_or_none(cls, session: AsyncSession, **kwargs: Unpack[QueryParams]) -> Self | None:
        lookup = cls.query(**kwargs).limit(1)
        result = await session.scalar(lookup)
        return result

    async def get_connect_installation(self, session: AsyncSession) -> ConnectInstallationOrm:
        obj = await ConnectInstallationOrm.one_or_exception(
            session=session,
            product=AtlassianProduct.confluence,
            id=self.connect_installation_id,
        )
        return obj

    @property
    def document_client(self) -> "ConfluenceClient":
        return ConfluenceClient(self)


class ConfluenceClient(DocumentClient):
    confluence_destination: ConfluenceDestinationOrm

    def __init__(self, confluence_destination: ConfluenceDestinationOrm):
        self.confluence_destination = confluence_destination

    async def get_available_spaces(self, ctx: Optional[LogContext] = None) -> GetAvailableSpacesRequest.ResponseBody:
        response = await GetAvailableSpacesRequest.perform(
            ctx=ctx,
            origin=app_config.eave_origin,
            team_id=self.confluence_destination.team_id,
        )
        return response

    @override
    async def search_documents(self, *, query: str, ctx: Optional[LogContext] = None) -> list[DocumentSearchResult]:
        response = await SearchContentRequest.perform(
            ctx=ctx,
            origin=app_config.eave_origin,
            team_id=self.confluence_destination.team_id,
            input=SearchContentRequest.RequestBody(
                search_params=ConfluenceSearchParamsInput(space_key=self.confluence_destination.space_key, text=query),
            ),
        )

        async with database.async_session.begin() as db_session:
            connect_installation = await self.confluence_destination.get_connect_installation(session=db_session)

        base = connect_installation.base_url
        # TODO: Better handling of nil title
        return [
            DocumentSearchResult(
                title=result.title or "Document", url=(f"{base}{result.links.webui}" if result.links else base)
            )
            for result in response.results
        ]

    @override
    async def delete_document(self, *, document_id: str, ctx: Optional[LogContext] = None) -> None:
        await DeleteContentRequest.perform(
            ctx=ctx,
            origin=app_config.eave_origin,
            team_id=self.confluence_destination.team_id,
            input=DeleteContentRequest.RequestBody(
                content=DeleteContentInput(
                    content_id=document_id,
                ),
            ),
        )

    @override
    async def create_document(self, *, input: DocumentInput, ctx: Optional[LogContext] = None) -> DocumentMetadata:
        response = await CreateContentRequest.perform(
            ctx=ctx,
            origin=app_config.eave_origin,
            team_id=self.confluence_destination.team_id,
            input=CreateContentRequest.RequestBody(
                confluence_destination=ConfluenceDestinationInput(
                    space_key=self.confluence_destination.space_key,
                ),
                document=input,
            ),
        )

        return DocumentMetadata(
            id=response.content.id,
            url=response.content.url,
        )

    @override
    async def update_document(
        self, *, input: DocumentInput, document_id: str, ctx: Optional[LogContext] = None
    ) -> DocumentMetadata:
        response = await UpdateContentRequest.perform(
            ctx=ctx,
            origin=app_config.eave_origin,
            team_id=self.confluence_destination.team_id,
            input=UpdateContentRequest.RequestBody(
                content=UpdateContentInput(
                    id=document_id,
                    body=input.content,
                ),
            ),
        )

        return DocumentMetadata(
            id=response.content.id,
            url=response.content.url,
        )
