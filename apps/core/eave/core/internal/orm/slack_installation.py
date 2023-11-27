import strawberry.federation as sb
from datetime import datetime, timedelta
from typing import NotRequired, Optional, Self, Tuple, TypedDict, Unpack
from uuid import UUID
from sqlalchemy import Index, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

import eave.core.internal.oauth.slack
from eave.stdlib.core_api.models.slack import SlackInstallation, SlackInstallationPeek
from eave.stdlib.exceptions import MissingOAuthCredentialsError
from .resource_mutex import ResourceMutexOrm
from eave.stdlib.logging import eaveLogger

from .base import Base
from .util import UUID_DEFAULT_EXPR, make_team_composite_pk, make_team_fk


class SlackInstallationOrm(Base):
    __tablename__ = "slack_sources"
    __table_args__ = (
        make_team_composite_pk(table_name="slack_sources"),
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
    slack_team_name: Mapped[Optional[str]] = mapped_column()
    slack_team_id: Mapped[str] = mapped_column(unique=True, index=True)
    """team[id] from here: https://api.slack.com/methods/oauth.v2.access#examples"""
    # bot identification data for authorizing slack api calls
    bot_token: Mapped[str] = mapped_column()
    bot_token_exp: Mapped[Optional[datetime]] = mapped_column()
    bot_refresh_token: Mapped[Optional[str]] = mapped_column()
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        team_id: UUID,
        slack_team_id: str,
        bot_token: str,
        bot_refresh_token: Optional[str],
        bot_token_exp: Optional[datetime],
        slack_team_name: Optional[str] = None,
    ) -> Self:
        obj = cls(
            team_id=team_id,
            slack_team_id=slack_team_id,
            bot_token=bot_token,
            bot_refresh_token=bot_refresh_token,
            bot_token_exp=bot_token_exp,
            slack_team_name=slack_team_name,
        )
        session.add(obj)
        await session.flush()
        return obj

    async def refresh_token_or_exception(self, session: AsyncSession) -> None:
        """
        Checks if `bot_token` is still valid. If it is, no more action is taken.
        If it isn't valid, then we try to refresh the token and set the new values
        in the object instance.

        raises -- SlackApiError on auth errors unrelated to token expiration
                  InvalidAuthError when there is no `bot_refresh_token` set or if the refresh request fails
        """

        if not self.bot_refresh_token:
            raise MissingOAuthCredentialsError("SlackInstallationOrm refresh token")

        if self.bot_token_exp and self.bot_token_exp > (datetime.utcnow() + timedelta(minutes=60)):
            # no need to refresh yet.
            return

        # FIXME: This doesn't really help if a request comes in while the token is being refreshed.
        # The client will just get an error response. We could ask them to retry the request, or make them
        # wait until the refresh is completed.
        acquired = await ResourceMutexOrm.acquire(session=session, resource_id=self.id)
        if not acquired:
            return

        try:
            new_tokens = await eave.core.internal.oauth.slack.refresh_access_token_or_exception(
                refresh_token=self.bot_refresh_token,
            )

            if (access_token := new_tokens.get("access_token")) and (refresh_token := new_tokens.get("refresh_token")):
                eaveLogger.debug("Refreshing Slack auth tokens.")
                self.bot_token = access_token
                self.bot_refresh_token = refresh_token

                if expires_in := new_tokens.get("expires_in"):
                    self.bot_token_exp = datetime.utcnow() + timedelta(seconds=expires_in)
                else:
                    self.bot_token_exp = None  # Be sure we don't retain an old expire value

            else:
                raise MissingOAuthCredentialsError("slack access or refresh token")
        except Exception:
            eaveLogger.exception("Error while refreshing tokens")
        finally:
            await ResourceMutexOrm.release(session=session, resource_id=self.id)

    class _selectparams(TypedDict):
        slack_team_id: NotRequired[str]
        team_id: NotRequired[UUID]

    @classmethod
    def _build_select(cls, **kwargs: Unpack[_selectparams]) -> Select[Tuple[Self]]:
        lookup = select(cls).limit(1)
        slack_team_id = kwargs.get("slack_team_id")
        eave_team_id = kwargs.get("team_id")

        assert slack_team_id or eave_team_id, "Invalid parameters"

        if slack_team_id:
            lookup = lookup.where(cls.slack_team_id == slack_team_id)
        if eave_team_id:
            lookup = lookup.where(cls.team_id == eave_team_id)

        assert lookup.whereclause is not None, "Invalid parameters"
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

    @property
    def api_model(self) -> SlackInstallation:
        return SlackInstallation.from_orm(self)

    @property
    def api_model_peek(self) -> SlackInstallationPeek:
        return SlackInstallationPeek.from_orm(self)

@sb.type
class SlackInstallation:
    id: uuid.UUID = sb.field()
    team_id: uuid.UUID = sb.field()
    slack_team_id: str = sb.field()
    bot_token: str = sb.field()

    @classmethod
    def from_orm(cls, orm: SlackInstallationOrm) -> "SlackInstallation":
        return SlackInstallation(
            id=orm.id,
            team_id=orm.team_id,
            slack_team_id=orm.slack_team_id,
            bot_token=orm.bot_token,
        )

@sb.input
class SlackInstallationInput:
    slack_team_id: str = sb.field()
