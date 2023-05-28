from typing import List, Optional
import pydantic
from eave.stdlib.core_api import models
from eave.stdlib.core_api.models import ConfluenceSpace
from eave.stdlib.core_api.models.base import EaveBaseModel
from eave.stdlib.core_api.operations.base import BaseRequestBody, BaseResponseBody, Endpoint, EndpointConfiguration
from eave.stdlib.core_api.operations.forge import ForgeInstallation

## Github


class GithubInstallation(EaveBaseModel):
    id: pydantic.UUID4
    team_id: pydantic.UUID4
    """eave TeamOrm model id"""
    github_install_id: str

    class Config:
        orm_mode = True


class GithubInstallationInput(pydantic.BaseModel):
    github_install_id: str


class GetGithubInstallation(Endpoint):
    config = EndpointConfiguration(
        path="/integrations/github/query",
        auth_required=False,
        team_id_required=False,
    )

    class RequestBody(BaseRequestBody):
        github_integration: GithubInstallationInput

    class ResponseBody(BaseResponseBody):
        team: models.Team
        github_integration: GithubInstallation


## Slack


class SlackInstallation(EaveBaseModel):
    id: pydantic.UUID4
    team_id: pydantic.UUID4
    """eave TeamOrm model id"""
    slack_team_id: str
    bot_token: str

    class Config:
        orm_mode = True


class SlackInstallationInput(pydantic.BaseModel):
    slack_team_id: str


class GetSlackInstallation(Endpoint):
    config = EndpointConfiguration(
        path="/integrations/slack/query",
        auth_required=False,
        team_id_required=False,
    )

    class RequestBody(BaseRequestBody):
        slack_integration: SlackInstallationInput

    class ResponseBody(BaseResponseBody):
        team: models.Team
        slack_integration: SlackInstallation


##  Atlassian


class AtlassianInstallation(pydantic.BaseModel):
    id: pydantic.UUID4
    team_id: pydantic.UUID4
    """eave TeamOrm model id"""
    atlassian_cloud_id: str
    confluence_space_key: Optional[str]
    available_confluence_spaces: Optional[List[ConfluenceSpace]]
    oauth_token_encoded: str

    class Config:
        orm_mode = True


class AtlassianInstallationInput(pydantic.BaseModel):
    atlassian_cloud_id: str


class GetAtlassianInstallation(Endpoint):
    config = EndpointConfiguration(
        path="/integrations/atlassian/query",
        auth_required=False,
        team_id_required=False,
    )

    class RequestBody(BaseRequestBody):
        atlassian_integration: AtlassianInstallationInput

    class ResponseBody(BaseResponseBody):
        team: models.Team
        atlassian_integration: AtlassianInstallation


class UpdateAtlassianInstallationInput(pydantic.BaseModel):
    confluence_space_key: Optional[str]


class UpdateAtlassianInstallation(Endpoint):
    config = EndpointConfiguration(
        path="/integrations/atlassian/update",
        auth_required=False,
        team_id_required=False,
    )

    class RequestBody(BaseRequestBody):
        atlassian_integration: UpdateAtlassianInstallationInput

    class ResponseBody(BaseResponseBody):
        account: models.AuthenticatedAccount
        team: models.Team
        atlassian_integration: AtlassianInstallation


class Integrations(EaveBaseModel):
    """
    Key-value mapping of Integration to Installation info.
    The keys here will match the enum cases in enums.Integration
    """

    github: Optional[GithubInstallation]
    slack: Optional[SlackInstallation]
    forge: Optional[ForgeInstallation]
    atlassian: Optional[AtlassianInstallation]
