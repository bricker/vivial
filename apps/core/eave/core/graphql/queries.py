from typing import Optional
from uuid import UUID
import strawberry.federation as sb
from strawberry.unset import UNSET
from eave.core.graphql.types.atlassian import AtlassianInstallation, AtlassianInstallationResolvers
from eave.core.graphql.types.github_installation import GithubInstallation, GithubInstallationQueryInput, GithubInstallationResolvers
from eave.core.graphql.types.github_repos import GithubRepo, GithubRepoFeature, GithubRepoResolvers, GithubReposFeatureStateInput
import eave.core.internal.database as eave_db
from eave.core.internal.orm.github_installation import GithubInstallationOrm
from eave.core.internal.orm.github_repos import GithubRepoOrm
from eave.core.internal.orm.team import TeamOrm
from eave.core.graphql.types.team import Team, TeamResolvers

@sb.type
class Query:
    team: Team = sb.field(resolver=TeamResolvers.get_team)

    github_installation: Optional[GithubInstallation] = sb.field(resolver=GithubInstallationResolvers.get_github_installation_for_install_id)

    atlassian_installation: Optional[AtlassianInstallation] = sb.field(resolver=AtlassianInstallationResolvers.get_atlassian_installation_for_cloud_id)

    github_repos: list[GithubRepo] = sb.field(resolver=GithubRepoResolvers.get_github_repos_for_feature_state)
