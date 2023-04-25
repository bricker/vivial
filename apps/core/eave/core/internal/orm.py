from dataclasses import dataclass
import hashlib
import json
from ctypes import ArgumentError
from datetime import datetime, UTC
import time
from typing import NotRequired, Optional, ParamSpec, Required, Self, Tuple, TypedDict, Unpack
from uuid import UUID
import uuid
import eave.stdlib.core_api.enums

import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.operations as eave_ops
import eave.stdlib.jwt as eave_jwt
import oauthlib
import oauthlib.oauth2.rfc6749.tokens
from sqlalchemy import (
    ForeignKeyConstraint,
    Index,
    PrimaryKeyConstraint,
    Select,
    false,
    null,
    func,
    select,
    text,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import eave.stdlib.eave_origins as eave_origins

from . import database as eave_db
from .destinations import abstract as abstract_destination
from .destinations import confluence as confluence_destination
from .oauth import atlassian as atlassian_oauth
from .oauth import models as oauth_models

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
        stmt = select(cls).where(cls.team_id == team_id).where(cls.id == id).limit(1)

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
    source_platform: Mapped[eave.stdlib.core_api.enums.SubscriptionSourcePlatform] = mapped_column()
    source_event: Mapped[eave.stdlib.core_api.enums.SubscriptionSourceEvent] = mapped_column()
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


class SlackInstallationOrm(Base):
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
    slack_team_id: Mapped[str] = mapped_column(unique=True, index=True)
    """team[id] from here: https://api.slack.com/methods/oauth.v2.access#examples"""
    # bot identification data for authorizing slack api calls
    bot_token: Mapped[str] = mapped_column()
    bot_id: Mapped[str] = mapped_column()
    bot_user_id: Mapped[Optional[str]] = mapped_column(server_default=None)
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    class _selectparams(TypedDict):
        slack_team_id: NotRequired[str]
        team_id: NotRequired[UUID]

    @classmethod
    def _build_select(cls, **kwargs: Unpack[_selectparams]) -> Select[Tuple[Self]]:
        lookup = select(cls).limit(1)
        slack_team_id = kwargs.get("slack_team_id")
        eave_team_id = kwargs.get("team_id")
        if not slack_team_id and not eave_team_id:
            raise ArgumentError("at least one parameter is required")
        if slack_team_id:
            lookup = lookup.where(cls.slack_team_id == slack_team_id)
        if eave_team_id:
            lookup = lookup.where(cls.team_id == eave_team_id)

        assert lookup.whereclause is not None
        return lookup

    @classmethod
    async def one_or_none(cls, session: AsyncSession, **kwargs: Unpack[_selectparams]) -> Optional[Self]:
        lookup = cls._build_select(**kwargs)
        result = (await session.scalars(lookup)).one_or_none()
        return result

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, **kwargs: Unpack[_selectparams]) -> Self:
        lookup = cls._build_select(**kwargs)
        result = (await session.scalars(lookup)).one()
        return result


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

    class _selectparams(TypedDict):
        team_id: NotRequired[uuid.UUID]
        atlassian_cloud_id: NotRequired[str]

    @classmethod
    def _build_select(cls, **kwargs: Unpack[_selectparams]) -> Select[Tuple[Self]]:
        lookup = select(cls).limit(1)

        if (team_id := kwargs.get("team_id")) is not None:
            lookup = lookup.where(cls.team_id == team_id)

        if (atlassian_cloud_id := kwargs.get("atlassian_cloud_id")) is not None:
            lookup = lookup.where(cls.atlassian_cloud_id == atlassian_cloud_id)

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

    @property
    def oauth_token_decoded(self) -> oauthlib.oauth2.rfc6749.tokens.OAuth2Token:
        jsonv = json.loads(self.oauth_token_encoded)
        return oauthlib.oauth2.rfc6749.tokens.OAuth2Token(params=jsonv)

    @property
    def confluence_destination(self) -> confluence_destination.ConfluenceDestination:
        assert self.confluence_space is not None
        return confluence_destination.ConfluenceDestination(
            oauth_session=self.build_oauth_session(),
            atlassian_cloud_id=self.atlassian_cloud_id,
            space=self.confluence_space,
        )

    def build_oauth_session(self) -> atlassian_oauth.AtlassianOAuthSession:
        session = atlassian_oauth.AtlassianOAuthSession(
            token=self.oauth_token_decoded,
            token_updater=self.update_token,
        )

        return session

    def update_token(self, token: oauthlib.oauth2.rfc6749.tokens.OAuth2Token) -> None:
        """
        This function can't be async because it's called by OAuthSession.
        Therefore, We need to use a sync engine.
        """
        with eave_db.get_sync_session() as db_session:
            self.oauth_token_encoded = json.dumps(token)
            db_session.commit()

class GithubInstallationOrm(Base):
    __tablename__ = "github_installations"
    __table_args__ = (
        make_team_composite_pk(),
        make_team_fk(),
        Index(
            "eave_team_id_github_install_id",
            "team_id",
            "github_install_id",
            unique=True,
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    github_install_id: Mapped[str] = mapped_column(unique=True)
    # TODO: Oauth token storage
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())


class TeamOrm(Base):
    __tablename__ = "teams"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=UUID_DEFAULT_EXPR)
    name: Mapped[str]
    document_platform: Mapped[Optional[eave.stdlib.core_api.enums.DocumentPlatform]] = mapped_column(server_default=None)
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())
    beta_whitelisted: Mapped[bool] = mapped_column(server_default=false())

    subscriptions: Mapped[list["SubscriptionOrm"]] = relationship()

    async def get_document_destination(
        self, session: AsyncSession
    ) -> Optional[abstract_destination.DocumentDestination]:
        match self.document_platform:
            case None:
                return None

            case eave.stdlib.core_api.enums.DocumentPlatform.confluence:
                atlassian_installation = await AtlassianInstallationOrm.one_or_exception(
                    session=session,
                    team_id=self.id,
                )
                return atlassian_installation.confluence_destination

            case eave.stdlib.core_api.enums.DocumentPlatform.google_drive:
                raise NotImplementedError("google drive document destination is not yet implemented.")

            case eave.stdlib.core_api.enums.DocumentPlatform.eave:
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
        Index(
            None,
            "auth_provider",
            "auth_id",
            "oauth_token",
            unique=True,
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    auth_provider: Mapped[eave.stdlib.core_api.enums.AuthProvider] = mapped_column()
    """3rd party login provider"""
    auth_id: Mapped[str] = mapped_column()
    """userid from 3rd party auth_provider"""
    # TODO: Store refresh token also
    oauth_token: Mapped[str] = mapped_column()
    """oauth token from 3rd party"""
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    class _selectparams(TypedDict):
        id: NotRequired[uuid.UUID]
        exchange_offer: NotRequired[eave_ops.AccessTokenExchangeOfferInput]
        auth_info: NotRequired[eave_models.AuthInfo]

    @classmethod
    def _build_select(cls, **kwargs: Unpack[_selectparams]) -> Select[Tuple[Self]]:
        lookup = select(cls).limit(1)

        id = kwargs.get("id")
        exchange_offer = kwargs.get("exchange_offer")
        auth_info = kwargs.get("auth_info")

        if id is not None:
            lookup = lookup.where(cls.id == id)

        if exchange_offer is not None:
            lookup = (
                lookup
                .where(cls.auth_provider == exchange_offer.auth_provider)
                .where(cls.auth_id == exchange_offer.auth_id)
                .where(cls.oauth_token == exchange_offer.oauth_token)
            )

        if auth_info is not None:
            lookup = (
                lookup
                .where(cls.auth_provider == auth_info.provider)
                .where(cls.auth_id == auth_info.id)
            )

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

class AuthTokenOrm(Base):
    __tablename__ = "auth_tokens"
    __table_args__ = (
        make_team_composite_pk(),
        make_team_fk(),
        ForeignKeyConstraint(
            ["team_id", "account_id"],
            ["accounts.team_id", "accounts.id"],
        ),
        Index(
            "token_pair",
            "access_token",
            "refresh_token",
            unique=True,
        ),
    )

    team_id: Mapped[UUID] = mapped_column()
    id: Mapped[UUID] = mapped_column(server_default=UUID_DEFAULT_EXPR)
    account_id: Mapped[UUID] = mapped_column()
    access_token: Mapped[str] = mapped_column(index=True, unique=True)
    refresh_token: Mapped[str] = mapped_column(index=True, unique=True)
    jti: Mapped[str] = mapped_column()
    iss: Mapped[str] = mapped_column()
    aud: Mapped[str] = mapped_column()
    expires: Mapped[datetime] = mapped_column()
    invalidated: Mapped[Optional[datetime]] = mapped_column(server_default=None)
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    class _selectparams(TypedDict):
        access_token_hashed: Required[str]
        refresh_token_hashed: NotRequired[str]

    @classmethod
    def _build_select(cls, **kwargs: Unpack[_selectparams]) -> Select[Tuple[Self]]:
        access_token_hashed: str = kwargs["access_token_hashed"]
        refresh_token_hashed: str | None = kwargs.get("refresh_token_hashed")

        lookup = select(cls).where(cls.invalidated == null()).limit(1)
        lookup = lookup.where(cls.access_token == access_token_hashed)

        if refresh_token_hashed is not None:
            lookup = lookup.where(cls.refresh_token == refresh_token_hashed)

        assert lookup.whereclause is not None
        return lookup

    @classmethod
    async def one_or_exception(cls, session: AsyncSession, **kwargs: Unpack[_selectparams]) -> Self:
        lookup = cls._build_select(**kwargs)
        result = (await session.scalars(lookup)).one()
        return result

    @property
    def expired(self) -> bool:
        return datetime.utcnow() >= self.expires

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
