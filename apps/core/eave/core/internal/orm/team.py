from datetime import datetime
from typing import Any, Optional, Self, Sequence, Tuple, TypedDict, Unpack
from uuid import UUID
import sqlalchemy.sql
from eave.core.internal.document_client import DocumentClient
from eave.core.internal.orm.atlassian_installation import AtlassianInstallationOrm
from eave.core.internal.orm.confluence_destination import ConfluenceDestinationOrm
from eave.core.internal.orm.connect_installation import ConnectInstallationOrm
import eave.stdlib.util
from sqlalchemy import Row, Select, false, func, select
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
        query = (
            sqlalchemy.sql.select(
                TeamOrm, SlackInstallationOrm, GithubInstallationOrm, AtlassianInstallationOrm, ConnectInstallationOrm
            )
            .join(SlackInstallationOrm, TeamOrm.id == SlackInstallationOrm.team_id, isouter=True)
            .join(GithubInstallationOrm, TeamOrm.id == GithubInstallationOrm.team_id, isouter=True)
            .join(AtlassianInstallationOrm, TeamOrm.id == AtlassianInstallationOrm.team_id, isouter=True)
            .join(ConnectInstallationOrm, TeamOrm.id == ConnectInstallationOrm.team_id, isouter=True)
            .filter(TeamOrm.id == self.id)
        )

        # should contain up to 2 rows:
        # 1 w/ jira connectinstall and other w/ confluence connectinstall (other column data is same)
        query_res: Sequence[
            Row[
                Tuple[
                    TeamOrm,
                    SlackInstallationOrm,
                    GithubInstallationOrm,
                    AtlassianInstallationOrm,
                    ConnectInstallationOrm,
                ]
            ]
        ] = (await session.execute(query)).all()

        if len(query_res) > 2:
            # getting more than 2 results means our db structure has changed meaningfully,
            # without this code being updated
            eaveLogger.warning(
                f"Expected 2 or fewer rows of results from joined installations table, got {len(query_res)}",
            )

        slack_install: Optional[SlackInstallationOrm] = None
        github_install: Optional[GithubInstallationOrm] = None
        atlassian_install: Optional[AtlassianInstallationOrm] = None
        confluence_install: Optional[ConnectInstallationOrm] = None
        jira_install: Optional[ConnectInstallationOrm] = None

        def validate_data(curr: Any, next: Any) -> None:
            """
            Helper function to validate data consistency assumptions
            """
            if curr and not (curr == next):
                eaveLogger.error(
                    "Violation of assumption that integrations join table columns have the same values across rows"
                )

        for results_row in query_res:
            # we dont care about TeamOrm that is first in unpacking, so we ignore with _
            _, slack_tmp, github_tmp, atlassian_tmp, connect_tmp = results_row

            validate_data(slack_install, slack_tmp)
            slack_install = slack_tmp

            validate_data(github_install, github_tmp)
            github_install = github_tmp

            validate_data(atlassian_install, atlassian_tmp)
            atlassian_install = atlassian_tmp

            if connect_tmp:
                match connect_tmp.product:
                    case AtlassianProduct.confluence:
                        validate_data(confluence_install, connect_tmp)
                        confluence_install = connect_tmp
                    case AtlassianProduct.jira:
                        validate_data(jira_install, connect_tmp)
                        jira_install = connect_tmp

        return Integrations(
            slack_integration=slack_install.api_model_peek if slack_install else None,
            github_integration=github_install.api_model_peek if github_install else None,
            atlassian_integration=atlassian_install.api_model_peek if atlassian_install else None,
            confluence_integration=confluence_install.api_model_peek if confluence_install else None,
            jira_integration=jira_install.api_model_peek if jira_install else None,
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
