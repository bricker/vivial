import uuid

import strawberry
from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel

@strawberry.type
class GithubInstallation(BaseResponseModel):
    id: uuid.UUID
    team_id: uuid.UUID
    """eave TeamOrm model id"""
    github_install_id: str


GithubInstallationPeek = GithubInstallation
"""Type Alias for naming consistency with other integrations."""

@strawberry.input
class GithubInstallationInput:
    github_install_id: str
