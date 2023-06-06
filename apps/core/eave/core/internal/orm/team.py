from datetime import datetime
from typing import Optional, Self, Tuple, TypedDict, Unpack
from uuid import UUID
from eave.core.internal.document_client import DocumentClient
from eave.core.internal.orm.atlassian_installation import AtlassianInstallationOrm
from eave.core.internal.orm.confluence_destination import ConfluenceDestinationOrm
from eave.core.internal.orm.connect_installation import ConnectInstallationOrm
import eave.stdlib
from sqlalchemy import Select, false, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from eave.stdlib.core_api.models.connect import AtlassianProduct
from eave.stdlib.core_api.models.team import Destination, DocumentPlatform

from eave.stdlib.core_api.models.team import Team
from eave.stdlib.core_api.models.integrations import Integrations
from .base import Base
from .github_installation import GithubInstallationOrm
from .slack_installation import SlackInstallationOrm
from .subscription import SubscriptionOrm
from .util import UUID_DEFAULT_EXPR
from eave.stdlib.logging import eaveLogger


class TeamOrm(Base):
    __tablename__ = "teams"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=UUID_DEFAULT_EXPR)
    name: Mapped[str]
    document_platform: Mapped[Optional[DocumentPlatform]] = mapped_column(server_default=None)
    created: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    updated: Mapped[Optional[datetime]] = mapped_column(server_default=None, onupdate=func.current_timestamp())
    beta_whitelisted: Mapped[bool] = mapped_column(server_default=false())

    subscriptions: Mapped[list[SubscriptionOrm]] = relationship()

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        name: str,
        document_platform: Optional[DocumentPlatform] = None,
        beta_whitelisted: bool = False,
    ) -> Self:
        obj = cls(
            name=name,
            document_platform=document_platform,
            beta_whitelisted=beta_whitelisted,
        )
        session.add(obj)
        await session.flush()
        return obj

    @property
    def api_model(self) -> Team:
        return Team.from_orm(self)

    async def get_document_client(self, session: AsyncSession) -> Optional[DocumentClient]:
        match self.document_platform:
            case None:
                return None

            case DocumentPlatform.confluence:
                connect_installation = await ConnectInstallationOrm.one_or_exception(
                    session=session,
                    product=AtlassianProduct.confluence,
                    team_id=self.id,
                )
                destination = await ConfluenceDestinationOrm.one_or_none(
                    session=session,
                    connect_installation_id=connect_installation.id,
                )

                if not destination:
                    eaveLogger.warning(f"No destination configured for team {self.id}")
                    return None

                return destination.document_client

            case DocumentPlatform.google_drive:
                raise NotImplementedError("google drive document destination is not yet implemented.")

            case DocumentPlatform.eave:
                raise NotImplementedError("eave document destination is not yet implemented.")

            case _:
                raise NotImplementedError(f"unsupported document platform: {self.document_platform}")

    class QueryParams(TypedDict):
        team_id: UUID | str

    @classmethod
    def query(cls, **kwargs: Unpack[QueryParams]) -> Select[Tuple[Self]]:
        team_id = eave.stdlib.util.ensure_uuid(kwargs["team_id"])
        lookup = select(cls).where(cls.id == team_id)
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

    async def get_integrations(self, session: AsyncSession) -> Integrations:
        slack_installation = await SlackInstallationOrm.one_or_none(session=session, team_id=self.id)
        github_installation = await GithubInstallationOrm.one_or_none(session=session, team_id=self.id)
        atlassian_installation = await AtlassianInstallationOrm.one_or_none(session=session, team_id=self.id)
        confluence_installation = await ConnectInstallationOrm.one_or_none(
            session=session, team_id=self.id, product=AtlassianProduct.confluence
        )
        jira_installation = await ConnectInstallationOrm.one_or_none(
            session=session, team_id=self.id, product=AtlassianProduct.jira
        )

        return Integrations(
            slack_integration=slack_installation.api_model_peek if slack_installation else None,
            github_integration=github_installation.api_model_peek if github_installation else None,
            atlassian_integration=atlassian_installation.api_model_peek if atlassian_installation else None,
            confluence_integration=confluence_installation.api_model_peek if confluence_installation else None,
            jira_integration=jira_installation.api_model_peek if jira_installation else None,
        )

    async def get_destination(self, session: AsyncSession) -> Destination | None:
        """
        Although a Team can currently only have one destination, the Destinations object acts as a
        container where the destination object lives under its own key.
        """
        match self.document_platform:
            case None:
                return None

            case DocumentPlatform.confluence:
                destination = await ConfluenceDestinationOrm.one_or_none(
                    session=session,
                    team_id=self.id,
                )

                if not destination:
                    eaveLogger.warning(f"No destination configured for team {self.id}")
                    return None

                return Destination(confluence_destination=destination.api_model)

            case _:
                raise NotImplementedError(f"unsupported document platform: {self.document_platform}")
