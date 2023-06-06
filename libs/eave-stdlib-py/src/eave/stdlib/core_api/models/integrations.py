import enum
from typing import Optional

from eave.stdlib.core_api.models.team import ConfluenceDestination
from .atlassian import AtlassianInstallation, AtlassianInstallationPeek
from .github import GithubInstallation, GithubInstallationPeek
from .slack import SlackInstallation, SlackInstallationPeek
from .connect import ConnectInstallation, ConnectInstallationPeek
from . import BaseResponseModel


class Integration(enum.StrEnum):
    """
    Apps that a Team can integrate with.
    """

    slack = "slack"
    github = "github"
    atlassian = "atlassian"
    confluence = "confluence"
    jira = "jira"


class Integrations(BaseResponseModel):
    github_integration: Optional[GithubInstallationPeek]
    slack_integration: Optional[SlackInstallationPeek]
    atlassian_integration: Optional[AtlassianInstallationPeek]
    confluence_integration: Optional[ConnectInstallationPeek]
    jira_integration: Optional[ConnectInstallationPeek]
