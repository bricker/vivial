import enum
import json
from datetime import datetime
from functools import cache, cached_property
from typing import Optional, ParamSpec, Self, Tuple, cast
from uuid import UUID, uuid4

import atlassian
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.operations as eave_ops
import eave.stdlib.openai_client
import eave.stdlib.util as eave_util
import oauthlib
import oauthlib.oauth2.rfc6749.tokens
import requests_oauthlib
from sqlalchemy import (
    ForeignKeyConstraint,
    Index,
    PrimaryKeyConstraint,
    Select,
    false,
    func,
    select,
    text,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from . import (
    database as eave_db,
)
from .oauth import (
    atlassian as atlassian_oauth,
    models as oauth_models,
)
from .config import app_config
from .destinations import (
    confluence as confluence_destination,
    abstract as abstract_destination,
)

UUID_DEFAULT_EXPR = text("(gen_random_uuid())")

P = ParamSpec("P")


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

    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    visitor_id: Mapped[Optional[UUID]] = mapped_column()
    email: Mapped[str] = mapped_column()
    opaque_input: Mapped[Optional[str]] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())

    @classmethod
    async def one_or_none(cls, session: AsyncSession, email: str) -> Optional["AccessRequestOrm"]:
        statement = select(cls).where(cls.email == email).limit(1)

        access_request = await session.scalar(statement)
        return access_request


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
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    document_id: Mapped[str] = mapped_column()
    document_url: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def one_or_exception(cls, team_id: UUID, id: UUID, session: AsyncSession) -> "DocumentReferenceOrm":
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
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    source_platform: Mapped[eave_models.SubscriptionSourcePlatform] = mapped_column()
    source_event: Mapped[eave_models.SubscriptionSourceEvent] = mapped_column()
    source_id: Mapped[str] = mapped_column()
    document_reference_id: Mapped[Optional[UUID]] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    async def get_document_reference(self, session: AsyncSession) -> Optional[DocumentReferenceOrm]:
        if self.document_reference_id is None:
            return None

        result = await DocumentReferenceOrm.one_or_exception(
            team_id=self.team_id,
            id=self.document_reference_id,
            session=session,
        )
        return result

    @property
    def source(self) -> eave_models.SubscriptionSource:
        return eave_models.SubscriptionSource(
            platform=self.source_platform,
            event=self.source_event,
            id=self.source_id,
        )

    @source.setter
    def source(self, source: eave_models.SubscriptionSource) -> None:
        self.source_platform = source.platform
        self.source_event = source.event
        self.source_id = source.id

    @classmethod
    async def one_or_none(
        cls, session: AsyncSession, team_id: UUID, source: eave_models.SubscriptionSource
    ) -> Optional[Self]:
        lookup = cls._select_one(team_id=team_id, source=source)
        subscription = await session.scalar(lookup)
        return subscription

    @classmethod
    async def one_or_exception(
        cls, session: AsyncSession, team_id: UUID, source: eave_models.SubscriptionSource
    ) -> Self:
        lookup = cls._select_one(team_id=team_id, source=source)
        subscription = (await session.scalars(lookup)).one()
        return subscription

    @classmethod
    def _select_one(cls, team_id: UUID, source: eave_models.SubscriptionSource) -> Select[Tuple[Self]]:
        lookup = (
            select(cls)
            .where(cls.team_id == team_id)
            .where(cls.source_platform == source.platform)
            .where(cls.source_event == source.event)
            .where(cls.source_id == source.id)
            .limit(1)
        )
        return lookup

class SlackSource(Base):
    __tablename__ = "slack_sources"
    __table_args__ = (
        make_team_composite_pk(),
        make_team_fk(),
        Index(
            "slack_team_id_eave_team_id",
            "team_id",
            "slack_team_id",
            unique=True,
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    """eave TeamOrm id"""
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    slack_team_id: Mapped[str] = mapped_column(unique=True)
    """team[id] from here: https://api.slack.com/methods/oauth.v2.access#examples"""

    # bot identification data for authorizing slack api calls
    bot_token: Mapped[str] = mapped_column()
    bot_id: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def one_or_none(cls, session: AsyncSession, team_id: UUID) -> Optional[Self]:
        lookup = select(cls).where(cls.team_id == team_id).limit(1)
        source: Self | None = (await session.scalars(lookup)).one_or_none()
        return source


class AtlassianInstallationOrm(Base):
    __tablename__ = "atlassian_installations"
    __table_args__ = (
        make_team_composite_pk(),
        make_team_fk(),
        Index(
            "eave_team_id_atlassian_team_id",
            "team_id",
            "atlassian_cloud_id",
            unique=True,
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    atlassian_cloud_id: Mapped[str] = mapped_column(unique=True)
    confluence_space: Mapped[Optional[str]] = mapped_column()
    oauth_token_encoded: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @property
    def oauth_token_decoded(self) -> oauthlib.oauth2.rfc6749.tokens.OAuth2Token:
        jsonv = json.loads(self.oauth_token_encoded)
        return oauthlib.oauth2.rfc6749.tokens.OAuth2Token(params=jsonv)

    def build_oauth_session(self) -> atlassian_oauth.AtlassianOAuthSession:
        session = atlassian_oauth.AtlassianOAuthSession(
            token=self.oauth_token_decoded,
            token_updater=self.update_token,
        )

        return session

    def update_token(self, token: oauthlib.oauth2.rfc6749.tokens.OAuth2Token) -> None:
        with eave_db.get_sync_session() as db_session:
            self.oauth_token_encoded = json.dumps(token)
            db_session.commit()

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, team_id: UUID) -> Self:
        lookup = select(cls).where(cls.team_id == team_id).limit(1)
        source = (await session.scalars(lookup)).one()
        return source

    @classmethod
    async def one_or_none(cls, session: AsyncSession, team_id: UUID) -> Optional[Self]:
        lookup = select(cls).where(cls.team_id == team_id).limit(1)
        source = (await session.scalars(lookup)).one_or_none()
        return source

    @classmethod
    async def one_or_none_by_atlassian_cloud_id(cls, session: AsyncSession, atlassian_cloud_id: str) -> Optional[Self]:
        lookup = select(cls).where(cls.atlassian_cloud_id == atlassian_cloud_id).limit(1)
        result: Self | None = (await session.scalars(lookup)).one_or_none()
        return result

class TeamOrm(Base):
    __tablename__ = "teams"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=UUID_DEFAULT_EXPR)
    name: Mapped[str]
    document_platform: Mapped[Optional[eave_models.DocumentPlatform]] = mapped_column(server_default=None)
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())
    beta_whitelisted: Mapped[bool] = mapped_column(server_default=false())

    subscriptions: Mapped[list["SubscriptionOrm"]] = relationship()

    async def get_document_destination(self, session: AsyncSession) -> Optional[abstract_destination.DocumentDestination]:
        match self.document_platform:
            case None:
                return None

            case eave_models.DocumentPlatform.confluence:
                atlassian_installation = await AtlassianInstallationOrm.one_or_exception(
                    session=session,
                    team_id=self.id,
                )

                return confluence_destination.ConfluenceDestination(atlassian_installation=atlassian_installation)

            case eave_models.DocumentPlatform.google_drive:
                raise NotImplementedError("google drive document destination is not yet implemented.")

            case eave_models.DocumentPlatform.eave:
                raise NotImplementedError("eave document destination is not yet implemented.")

            case _:
                raise NotImplementedError(f"unsupported document platform: {self.document_platform}")

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, team_id: UUID) -> Self:
        lookup = select(cls).where(cls.id == team_id).limit(1)
        team = (await session.scalars(lookup)).one()  # throws if not exists
        return team


class AccountOrm(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        make_team_composite_pk(),
        make_team_fk(),
        Index(
            "auth_provider_auth_id",
            "auth_provider",
            "auth_id",
            unique=True,
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    auth_provider: Mapped[oauth_models.AuthProvider] = mapped_column()
    """3rd party login provider"""
    auth_id: Mapped[str] = mapped_column()
    """userid from 3rd party auth_provider"""
    # TODO: Store refresh token also
    oauth_token: Mapped[str] = mapped_column()
    """oauth token from 3rd party"""
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, auth_provider: oauth_models.AuthProvider, auth_id: str) -> Self:
        lookup = cls._select_one(auth_provider=auth_provider, auth_id=auth_id)
        account = (await session.scalars(lookup)).one()
        return account

    @classmethod
    async def one_or_none(cls, session: AsyncSession, auth_provider: oauth_models.AuthProvider, auth_id: str) -> Self | None:
        lookup = cls._select_one(auth_provider=auth_provider, auth_id=auth_id)
        account = await session.scalar(lookup)
        return account

    @classmethod
    def _select_one(cls, auth_provider: oauth_models.AuthProvider, auth_id: str) -> Select[Tuple[Self]]:
        lookup = select(cls).where(cls.auth_provider == auth_provider).where(cls.auth_id == auth_id).limit(1)
        return lookup


# class EmbeddingsOrm(Base):
#     __tablename__ = "embeddings"
#     __table_args__ = (
#         make_team_composite_pk(),
#         make_team_fk(),
#         make_team_composite_fk("document_reference_id", "document_references"),
#     )

#     team_id: Mapped[UUID] = mapped_column()
#     id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
#     vector: Mapped[str] = mapped_column()  # comma-separated list of vector values (floats)
#     document_reference_id: Mapped[UUID] = mapped_column()
#     created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
#     updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())
