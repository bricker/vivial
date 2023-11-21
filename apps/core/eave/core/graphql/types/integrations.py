import enum
from typing import Optional

import strawberry.federation as sb
from eave.core.graphql.types.atlassian import AtlassianInstallation
from eave.core.graphql.types.connect_installation import ConnectInstallation

from eave.core.graphql.types.slack_installation import SlackInstallation

from .github_installation import GithubInstallation

@sb.enum
class Integration(enum.StrEnum):
    """
    Apps that a Team can integrate with.
    """

    slack = "slack"
    github = "github"
    atlassian = "atlassian"
    confluence = "confluence"
    jira = "jira"

@sb.type
class Integrations:
    github_integration: Optional[GithubInstallation] = sb.field(default=None)
    slack_integration: Optional[SlackInstallation] = sb.field(default=None)
    atlassian_integration: Optional[AtlassianInstallation] = sb.field(default=None)
    confluence_integration: Optional[ConnectInstallation] = sb.field(default=None)
    jira_integration: Optional[ConnectInstallation] = sb.field(default=None)
