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

import eave.internal.confluence
import eave.internal.openai
import eave.internal.util
from eave.internal.confluence import ConfluencePage
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
        """
        Atlassian Python API Docs: https://atlassian-python-api.readthedocs.io/
        """
        return atlassian.Confluence(
            url=self.url,
            username=self.api_username,
            password=self.api_key,
        )

    @property
    @cache
    def confluence_context(self) -> eave.internal.confluence.ConfluenceContext:
        return eave.internal.confluence.ConfluenceContext(base_url=self.url)

    async def create_document(self, document: DocumentContentInput, session: AsyncSession) -> DocumentReferenceOrm:
        confluence_page = await self.get_or_create_confluence_page(document=document)

        url = None
        if confluence_page.links is not None and confluence_page.links.tinyui_url is not None:
            url = confluence_page.links.tinyui_url

        document_reference = DocumentReferenceOrm(
            team_id=self.team_id,
            document_id=confluence_page.id,
            document_url=url,
        )

        session.add(document_reference)
        return document_reference

    async def update_document(
        self, document: DocumentContentInput, document_reference: DocumentReferenceOrm
    ) -> DocumentReferenceOrm:
        """
        Update an existing Confluence document with the new body.
        Notably, the title and parent are not changed.
        """
        existing_page = await self.get_confluence_page_by_id(document_reference=document_reference)
        if existing_page is None:
            # TODO: This page was probably deleted. Remove it from our database?
            raise NotImplementedError()

        # TODO: Use a different body format? Currently it will probably return the "storage" format,
        # which is XML (HTML), and probably not great for an OpenAI prompt.
        if existing_page.body is not None and existing_page.body.content is not None:
            # TODO: Token counting
            prompt = (
                f"{eave.internal.openai.PROMPT_PREFIX}\n"
                "Combine the following two documents together such that all important information is retained, "
                "but duplicate, unnecessary, irrelevant, or outdated information is removed.\n\n"
                "###\n\n"
                "=== Document 1: ===\n\n"
                f"{existing_page.body.content}\n\n"
                "=== Document 2: ===\n\n"
                f"{document.content}\n\n"
                "###\n\n"
                "=== Result: ===\n\n"
            )
            openai_params = eave.internal.openai.CompletionParameters(
                temperature=0.2,
                prompt=prompt,
            )
            resolved_document_body = await eave.internal.openai.summarize(params=openai_params)
            assert resolved_document_body is not None
        else:
            resolved_document_body = document.content

        response = self.confluence_client().update_page(
            page_id=document_reference.document_id,
            representation="wiki",
            title=existing_page.title,
            body=resolved_document_body,
        )
        assert response is not None
        return document_reference

    async def get_or_create_confluence_page(self, document: DocumentContentInput) -> ConfluencePage:
        existing_page = await self.get_confluence_page_by_title(document=document)
        if existing_page is not None:
            return existing_page

        parent_page = None
        if document.parent is not None:
            parent_page = await self.get_or_create_confluence_page(document=document.parent)

        response = self.confluence_client().create_page(
            space=self.space,
            representation="wiki",
            title=document.title,
            body=document.content,
            parent_id=parent_page.id if parent_page is not None else None,
        )
        assert response is not None

        json = cast(eave.internal.util.JsonObject, response)
        page = ConfluencePage(json, self.confluence_context)
        return page

    async def get_confluence_page_by_id(self, document_reference: DocumentReferenceOrm) -> ConfluencePage | None:
        response = self.confluence_client().get_page_by_id(
            page_id=document_reference.document_id,
            expand=["history"],
        )
        if response is None:
            return None

        json = cast(eave.internal.util.JsonObject, response)
        page = ConfluencePage(json, self.confluence_context)
        return page

    async def get_confluence_page_by_title(self, document: DocumentContentInput) -> ConfluencePage | None:
        response = self.confluence_client().get_page_by_title(
            space=self.space,
            title=document.title,
        )
        if response is None:
            return None

        json = cast(eave.internal.util.JsonObject, response)
        page = ConfluencePage(json, self.confluence_context)
        return page


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


# class EmbeddingsOrm(Base):
#     __tablename__ = "embeddings"
#     __table_args__ = (
#         make_team_composite_pk(),
#         make_team_fk(),
#         make_team_composite_fk("document_reference_id", "document_references"),
#     )

#     team_id: Mapped[UUID] = mapped_column()
#     id: Mapped[UUID] = mapped_column(default=uuid4)
#     vector: Mapped[str] = mapped_column()  # comma-separated list of vector values (floats)
#     document_reference_id: Mapped[UUID] = mapped_column()
#     created: Mapped[datetime] = mapped_column(default=datetime.utcnow)
#     updated: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)


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
