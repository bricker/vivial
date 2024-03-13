import uuid
from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel


class GithubInstallation(BaseResponseModel):
    id: uuid.UUID
    team_id: uuid.UUID
    """eave TeamOrm model id"""
    github_install_id: str


GithubInstallationPeek = GithubInstallation
"""Type Alias for naming consistency with other integrations."""


class GithubInstallationQueryInput(BaseInputModel):
    github_install_id: str
