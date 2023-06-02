import enum
from typing import Optional
from .atlassian import AtlassianInstallation
from .forge import ForgeInstallation
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
    forge = "forge"
    atlassian = "atlassian"
    confluence = 'confluence'
    jira = 'jira'


class Integrations(BaseResponseModel):
    github_integration: Optional[GithubInstallation]
    slack_integration: Optional[SlackInstallation]
    forge_integration: Optional[ForgeInstallation]
    atlassian_integration: Optional[AtlassianInstallation]
    confluence_integration: Optional[ConnectInstallation]
    jira_integration: Optional[ConnectInstallation]
