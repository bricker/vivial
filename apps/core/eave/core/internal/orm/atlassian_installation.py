import strawberry.federation as sb
import asyncio
from dataclasses import dataclass
import json
import uuid
from datetime import datetime
from typing import Callable, NotRequired, Optional, Self, Tuple, TypedDict, Unpack
from uuid import UUID

import oauthlib.oauth2.rfc6749.tokens
from sqlalchemy import Index, ScalarResult, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from strawberry.unset import UNSET

from eave.stdlib.core_api.models.atlassian import AtlassianInstallation, AtlassianInstallationPeek

from .. import database as eave_db
from ..oauth import atlassian as atlassian_oauth
from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_composite_pk, make_team_fk


class AtlassianInstallationOrm(Base):
    __tablename__ = "atlassian_installations"
    __table_args__ = (
        make_team_composite_pk(table_name="atlassian_installations"),
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
    atlassian_site_name: Mapped[Optional[str]] = mapped_column()
    atlassian_cloud_id: Mapped[str] = mapped_column(unique=True)
    """DEPRECATED"""
    confluence_space_key: Mapped[Optional[str]] = mapped_column("confluence_space")
    """DEPRECATED"""
    oauth_token_encoded: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @dataclass
    class QueryParams:
        id: uuid.UUID = UNSET
        team_id: uuid.UUID = UNSET
        atlassian_cloud_id: str = UNSET

    @classmethod
    def _build_query(cls, params: QueryParams) -> Select[Tuple[Self]]:
        lookup = select(cls)

        if params.id:
            lookup = lookup.where(cls.id == params.id)

        if params.team_id:
            lookup = lookup.where(cls.team_id == params.team_id)

        if params.atlassian_cloud_id:
            lookup = lookup.where(cls.atlassian_cloud_id == params.atlassian_cloud_id)

        assert lookup.whereclause is not None, "Invalid parameters"
        return lookup

    @classmethod
    async def query(cls, session: AsyncSession, params: QueryParams) -> ScalarResult[Self]:
        lookup = cls._build_query(params=params)
        results = await session.scalars(lookup)
        return results

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: uuid.UUID,
        atlassian_cloud_id: str,
        oauth_token_encoded: str,
        atlassian_site_name: Optional[str] = None,
    ) -> Self:
        obj = cls(
            team_id=team_id,
            atlassian_cloud_id=atlassian_cloud_id,
            oauth_token_encoded=oauth_token_encoded,
            atlassian_site_name=atlassian_site_name,
        )
        session.add(obj)
        await session.flush()
        return obj

    @property
    def oauth_token_decoded(self) -> oauthlib.oauth2.rfc6749.tokens.OAuth2Token:
        jsonv = json.loads(self.oauth_token_encoded)
        return oauthlib.oauth2.rfc6749.tokens.OAuth2Token(params=jsonv)

    def build_oauth_session(self) -> atlassian_oauth.AtlassianOAuthSession:
        session = atlassian_oauth.AtlassianOAuthSession(
            token=self.oauth_token_decoded,
            token_updater=self.token_updater_factory(),
        )

        return session

    _tasks = set[asyncio.Task[None]]()

    def token_updater_factory(self) -> Callable[[oauthlib.oauth2.rfc6749.tokens.OAuth2Token], None]:
        def token_updater(token: oauthlib.oauth2.rfc6749.tokens.OAuth2Token) -> None:
            # FIXME: This just updates the token in the background, which could cause a race condition.
            coro = AtlassianInstallationOrm.update_token(id=self.id, token=token)
            task = asyncio.create_task(coro)
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)

        return token_updater

    @classmethod
    async def update_token(cls, id: uuid.UUID, token: oauthlib.oauth2.rfc6749.tokens.OAuth2Token) -> None:
        async with eave_db.async_session.begin() as db_session:
            query = select(cls).where(cls.id == id)
            record = await db_session.scalar(query)
            if record:
                record.oauth_token_encoded = json.dumps(token)
                await db_session.commit()
