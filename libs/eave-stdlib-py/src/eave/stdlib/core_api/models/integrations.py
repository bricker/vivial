import enum
from typing import Optional
from .atlassian import AtlassianInstallation
from .github import GithubInstallation
from .slack import SlackInstallation
from .connect import ConnectInstallation
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
    github_integration: Optional[GithubInstallation]
    slack_integration: Optional[SlackInstallation]
    atlassian_integration: Optional[AtlassianInstallation]
    confluence_integration: Optional[ConnectInstallation]
    jira_integration: Optional[ConnectInstallation]
