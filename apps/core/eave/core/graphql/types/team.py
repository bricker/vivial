import strawberry.federation as sb
import enum
import uuid

from strawberry.unset import UNSET
from eave.core.graphql.types.api_documentation_job import ApiDocumentationJob, ApiDocumentationJobResolvers
from eave.core.graphql.types.atlassian import AtlassianInstallation, AtlassianInstallationResolvers
from eave.core.graphql.types.connect_installation import ConnectInstallation, ConnectInstallationResolvers
from eave.core.graphql.types.documents import DocumentResolvers, DocumentSearchResult
from eave.core.graphql.types.github_documents import GithubDocument, GithubDocumentResolvers
from eave.core.graphql.types.github_installation import GithubInstallation, GithubInstallationResolvers
from eave.core.graphql.types.github_repos import GithubRepo, GithubRepoResolvers
from eave.core.graphql.types.mutation_result import MutationResult
from eave.core.graphql.types.slack_installation import SlackInstallation, SlackInstallationResolvers
from eave.core.graphql.types.subscriptions import Subscription, SubscriptionResolvers
import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
from eave.core.internal.orm.github_repos import GithubRepoOrm
from eave.core.internal.orm.team import TeamOrm

from typing import Optional

@sb.enum
class DocumentPlatform(enum.StrEnum):
    eave = "eave"
    confluence = "confluence"
    google_drive = "google_drive"

@sb.type(keys=["id"])
class ConfluenceDestination:
    id: uuid.UUID = sb.field()
    space_key: Optional[str] = sb.field()

    @classmethod
@sb.type
class Destination:
    confluence_destination: Optional[ConfluenceDestination]

@sb.type(keys=["id"])
class AnalyticsTeam:
    id: uuid.UUID = sb.field()
    name: str = sb.field()
    document_platform: Optional[DocumentPlatform] = sb.field()

@sb.type(keys=["id"])
class Team:
    id: uuid.UUID = sb.field()
    name: str = sb.field()
    document_platform: Optional[DocumentPlatform] = sb.field()

    @classmethod
    def from_orm(cls, orm: TeamOrm) -> "Team":
        return Team(
            id=orm.id,
            name=orm.name,
            document_platform=DocumentPlatform(value=orm.document_platform) if orm.document_platform else None,
        )

    github_documents: list[GithubDocument] = sb.field(resolver=GithubDocumentResolvers.get_github_documents)
    github_repos: list[GithubRepo] = sb.field(resolver=GithubRepoResolvers.get_github_repos_for_team)
    github_repos_feature_states_match: bool = sb.field(resolver=GithubRepoResolvers.get_github_repos_feature_states_match)
    github_installation: Optional[GithubInstallation] = sb.field(resolver=GithubInstallationResolvers.get_github_installation_for_team)
    atlassian_installation: Optional[AtlassianInstallation] = sb.field(resolver=AtlassianInstallationResolvers.get_atlassian_installation_for_team)
    confluence_installation: Optional[ConnectInstallation] = sb.field(resolver=ConnectInstallationResolvers.get_confluence_installation_for_team)
    jira_installation: Optional[ConnectInstallation] = sb.field(resolver=ConnectInstallationResolvers.get_jira_installation_for_team)
    slack_installation: Optional[SlackInstallation] = sb.field(resolver=SlackInstallationResolvers.get_slack_installation_for_team)
    api_documentation_jobs: list[ApiDocumentationJob] = sb.field(resolver=ApiDocumentationJobResolvers.get_api_documentation_jobs)
    documents: list[DocumentSearchResult] = sb.field(resolver=DocumentResolvers.search_documents)
    subscription: Optional[Subscription] = sb.field(resolver=SubscriptionResolvers.get_subscription)

@sb.type
class ConfluenceDestinationMutationResult(MutationResult):
    confluence_destination: ConfluenceDestination

@sb.input
class ConfluenceDestinationInput:
    space_key: str = sb.field()

@sb.input
class TeamInput:
    name: Optional[str] = sb.field()
    document_platform: Optional[str] = sb.field()

class TeamResolvers:
    @staticmethod
    async def get_team(id: uuid.UUID) -> Team:
        async with eave_db.async_session.begin() as db_session:
            eave_team_orm = await TeamOrm.one_or_exception(
                session=db_session, team_id=id,
            )

            return Team.from_orm(eave_team_orm)

    @staticmethod
    async def upsert_confluence_destination(team_id: uuid.UUID, input: ConfluenceDestinationInput) -> ConfluenceDestinationMutationResult:
        async with database.async_session.begin() as db_session:
            team = await TeamOrm.one_or_exception(session=db_session, team_id=unwrap(eave_state.ctx.eave_team_id))

            connect_installation = await ConnectInstallationOrm.one_or_exception(
                session=db_session,
                product=AtlassianProduct.confluence,
                team_id=team.id,
            )

            dest = await ConfluenceDestinationOrm.upsert(
                session=db_session,
                team_id=team.id,
                connect_installation_id=connect_installation.id,
                space_key=input.confluence_destination.space_key,
            )

        return json_response(
            UpsertConfluenceDestinationAuthedRequest.ResponseBody(
                team=team.api_model,
                confluence_destination=dest.api_model,
            )
        )
