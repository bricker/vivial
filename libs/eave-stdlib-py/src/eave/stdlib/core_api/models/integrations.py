import enum
from typing import Optional

from .atlassian import AtlassianInstallationPeek
from .github import GithubInstallationPeek
from .slack import SlackInstallationPeek
from .connect import ConnectInstallationPeek
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
