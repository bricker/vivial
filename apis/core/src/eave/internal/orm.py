from datetime import datetime
from functools import cache
from typing import Optional, cast
from uuid import UUID, uuid4

import atlassian
from sqlalchemy import (
    ForeignKeyConstraint,
    Index,
    PrimaryKeyConstraint,
    UnicodeText,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from eave.internal.confluence import ConfluencePage
from eave.internal.json_object import JsonObject
from eave.public.shared import (
    DocumentContentInput,
    DocumentPlatform,
    SubscriptionSource,
    SubscriptionSourceEvent,
    SubscriptionSourcePlatform,
)


class Base(DeclarativeBase):
    pass


def make_team_composite_pk() -> PrimaryKeyConstraint:
    return PrimaryKeyConstraint(
        "team_id",
        "id",
    )


def make_team_fk() -> ForeignKeyConstraint:
    return ForeignKeyConstraint(
        ["team_id"],
        ["teams.id"],
    )


def make_team_composite_fk(fk_column: str, foreign_table: str) -> ForeignKeyConstraint:
    return ForeignKeyConstraint(["team_id", fk_column], [f"{foreign_table}.team_id", f"{foreign_table}.id"])


class AccessRequestOrm(Base):
    __tablename__ = "access_requests"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        Index(None, "visitor_id"),
        Index(None, "email", unique=True),
    )

    id: Mapped[UUID] = mapped_column(default=uuid4)
    visitor_id: Mapped[Optional[UUID]] = mapped_column()
    email: Mapped[str] = mapped_column()
    opaque_input: Mapped[Optional[str]] = mapped_column()
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    @classmethod
    async def find_one(cls, session: AsyncSession, email: str) -> Optional["AccessRequestOrm"]:
        statement = select(cls).where(cls.email == email).limit(1)

        access_request = await session.scalar(statement)
        return access_request


class PromptOrm(Base):
    __tablename__ = "prompts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    prompt: Mapped[str] = mapped_column(UnicodeText)
    response: Mapped[str] = mapped_column(UnicodeText)
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


class DocumentReferenceOrm(Base):
    __tablename__ = "document_references"
    __table_args__ = (
        make_team_composite_pk(),
        make_team_fk(),
        Index(
            "document_key",
            "team_id",
            "document_id",
            unique=True,
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(default=uuid4)
    document_id: Mapped[str] = mapped_column()
    document_url: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    async def find_one(cls, team_id: UUID, id: UUID, session: AsyncSession) -> "DocumentReferenceOrm":
        stmt = (
            select(DocumentReferenceOrm)
            .where(DocumentReferenceOrm.team_id == team_id)
            .where(DocumentReferenceOrm.id == id)
            .limit(1)
        )

        result = (await session.scalars(stmt)).one()
        return result


class SubscriptionOrm(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        make_team_composite_pk(),
        make_team_fk(),
        make_team_composite_fk("document_reference_id", "document_references"),
        Index(
            "source_key",
            "team_id",
            "source_platform",
            "source_event",
            "source_id",
            unique=True,
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(default=uuid4)
    source_platform: Mapped[SubscriptionSourcePlatform] = mapped_column()
    source_event: Mapped[SubscriptionSourceEvent] = mapped_column()
    source_id: Mapped[str] = mapped_column()
    document_reference_id: Mapped[Optional[UUID]] = mapped_column()
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    async def get_document_reference(self, session: AsyncSession) -> Optional[DocumentReferenceOrm]:
        if self.document_reference_id is None:
            return None

        result = await DocumentReferenceOrm.find_one(
            team_id=self.team_id,
            id=self.document_reference_id,
            session=session,
        )
        return result

    @property
    def source(self) -> SubscriptionSource:
        return SubscriptionSource(
            platform=self.source_platform,
            event=self.source_event,
            id=self.source_id,
        )

    @source.setter
    def source(self, source: SubscriptionSource) -> None:
        self.source_platform = source.platform
        self.source_event = source.event
        self.source_id = source.id

    @classmethod
    async def find_one(
        cls, session: AsyncSession, team_id: UUID, source: SubscriptionSource
    ) -> Optional["SubscriptionOrm"]:
        lookup = (
            select(cls)
            .where(cls.team_id == team_id)
            .where(cls.source_platform == source.platform)
            .where(cls.source_event == source.event)
            .where(cls.source_id == source.id)
            .limit(1)
        )

        subscription = await session.scalar(lookup)
        return subscription


class ConfluenceDestinationOrm(Base):
    __tablename__ = "confluence_destinations"
    __table_args__ = (
        make_team_composite_pk(),
        make_team_fk(),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(default=uuid4)
    url: Mapped[str] = mapped_column()
    api_username: Mapped[str] = mapped_column()
    api_key: Mapped[str] = mapped_column()
    space: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    @cache
    def confluence_client(self) -> atlassian.Confluence:
        return atlassian.Confluence(
            url=self.url,
            username=self.api_username,
            password=self.api_key,
        )

    async def create_document(self, document: DocumentContentInput, session: AsyncSession) -> DocumentReferenceOrm:
        response = self.confluence_client().create_page(
            space=self.space,
            representation="wiki",
            title=document.title,
            body=document.content,
        )
        if response is None:
            raise Exception("No response data returned from Confluence")

        json = cast(JsonObject, response)
        page = ConfluencePage(json)
        document_reference = DocumentReferenceOrm(
            team_id=self.team_id,
            document_id=page.id,
            document_url=page.links.tinyui_url,
        )

        session.add(document_reference)
        return document_reference

    async def update_document(
        self, document: DocumentContentInput, document_reference: DocumentReferenceOrm
    ) -> DocumentReferenceOrm:
        """
        This function pushes the given content to a new Confluence document.
        We currently leverage the Atlassian Python API to communicate with Confluence.

        Atlassian Python API Docs: https://atlassian-python-api.readthedocs.io/
        """
        response = self.confluence_client().update_page(
            page_id=document_reference.document_id,
            representation="wiki",
            title=document.title,
            body=document.content,
        )
        if response is None:
            raise Exception("No response data returned from Confluence")

        return document_reference


class TeamOrm(Base):
    __tablename__ = "teams"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    document_platform: Mapped[DocumentPlatform]
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    # api_keys: Mapped[list["ApiKeyOrm"]] = relationship(back_populates="team")
    subscriptions: Mapped[list["SubscriptionOrm"]] = relationship()

    async def get_document_destination(self, session: AsyncSession) -> ConfluenceDestinationOrm:
        match self.document_platform:
            case DocumentPlatform.confluence:
                stmt = select(ConfluenceDestinationOrm).where(ConfluenceDestinationOrm.team_id == self.id).limit(1)
                destination = (await session.scalars(stmt)).one()
                return destination

            case DocumentPlatform.eave:
                raise Exception("eave documentation platform not yet implemented.")

        raise Exception("unsupported platform")

    # @classmethod
    # def find_by_api_key(cls, api_key: UUID, session: AsyncSession):
    #     team = (
    #         select(TeamOrm)
    #         .join(ApiKeyOrm)
    #         .where(ApiKeyOrm.key == api_key)
    #     )

    @classmethod
    async def find_one(cls, session: AsyncSession, team_id: UUID) -> Optional["TeamOrm"]:
        lookup = select(cls).where(cls.id == team_id).limit(1)

        team = await session.scalar(lookup)
        return team


# class ApiKeyOrm(Base):
#     __tablename__ = "api_keys"
#     __table_args__ = (
#         make_team_composite_pk(),
#         make_team_fk(),
#         Index(None, "key", unique=True),
#         Index(None, "revoked"),
#         Index(
#             "not_revoked",
#             "key",
#             "revoked",
#         ),
#     )

#     team_id: Mapped[UUID] = mapped_column()
#     id: Mapped[UUID] = mapped_column(default=uuid4)
#     key: Mapped[UUID] = mapped_column(default=uuid4)
#     description: Mapped[Optional[str]]
#     accessed: Mapped[Optional[datetime]]
#     revoked: Mapped[Optional[datetime]] = mapped_column()
#     created: Mapped[datetime] = mapped_column(default=datetime.utcnow)
#     updated: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

#     team: Mapped["TeamOrm"] = relationship(back_populates="api_keys")

#     @classmethod
#     async def validate(cls, api_key: str, session: AsyncSession) -> TeamOrm:
#         uuid_key = UUID(api_key)
#         statement = (
#             select(cls)
#             .where(cls.key == uuid_key)
#             .where(cls.revoked == None)
#         )

#         record = (await session.scalars(statement)).one()
#         return record.team
