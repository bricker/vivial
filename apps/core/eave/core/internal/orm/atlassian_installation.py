import asyncio
import json
import uuid
from datetime import datetime
from typing import Callable, NotRequired, Optional, Self, Tuple, TypedDict, Unpack
from uuid import UUID

import oauthlib.oauth2.rfc6749.tokens
from sqlalchemy import Index, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from eave.stdlib.core_api.models.atlassian import AtlassianInstallation, AtlassianInstallationPeek
from eave.stdlib.core_api.models.atlassian import ConfluenceSpace

from .. import database as eave_db
from ..oauth import atlassian as atlassian_oauth
from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_composite_pk, make_team_fk


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
    atlassian_site_name: Mapped[Optional[str]] = mapped_column()
    atlassian_cloud_id: Mapped[str] = mapped_column(unique=True)
    """DEPRECATED"""
    confluence_space_key: Mapped[Optional[str]] = mapped_column("confluence_space")
    """DEPRECATED"""
    oauth_token_encoded: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    class _selectparams(TypedDict):
        id: NotRequired[uuid.UUID]
        team_id: NotRequired[uuid.UUID]
        atlassian_cloud_id: NotRequired[str]

    @classmethod
    def _build_select(cls, **kwargs: Unpack[_selectparams]) -> Select[Tuple[Self]]:
        lookup = select(cls).limit(1)

        if (id := kwargs.get("id")) is not None:
            lookup = lookup.where(cls.id == id)

        if (team_id := kwargs.get("team_id")) is not None:
            lookup = lookup.where(cls.team_id == team_id)

        if (atlassian_cloud_id := kwargs.get("atlassian_cloud_id")) is not None:
            lookup = lookup.where(cls.atlassian_cloud_id == atlassian_cloud_id)

        assert lookup.whereclause is not None, "Invalid parameters"
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

    @property
    def api_model(self) -> AtlassianInstallation:
        return AtlassianInstallation.from_orm(self)

    @property
    def api_model_peek(self) -> AtlassianInstallationPeek:
        return AtlassianInstallationPeek.from_orm(self)
