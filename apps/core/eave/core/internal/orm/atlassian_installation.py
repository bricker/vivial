from . import UUID_DEFAULT_EXPR, Base, make_team_composite_pk, make_team_fk
from .. import database as eave_db
from ..destinations import confluence as confluence_destination
from ..oauth import atlassian as atlassian_oauth


import oauthlib.oauth2.rfc6749.tokens
from sqlalchemy import Index, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column


import json
import uuid
from datetime import datetime
from typing import NotRequired, Optional, Self, Tuple, TypedDict, Unpack
from uuid import UUID


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
        Also why it is managing its own session.
        """
        with eave_db.sync_session.begin():
            self.oauth_token_encoded = json.dumps(token)