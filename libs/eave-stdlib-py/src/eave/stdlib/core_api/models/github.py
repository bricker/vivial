from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel


import pydantic


class GithubInstallation(BaseResponseModel):
    id: pydantic.UUID4
    team_id: pydantic.UUID4
    """eave TeamOrm model id"""
    github_install_id: str


class GithubInstallationInput(BaseInputModel):
    github_install_id: str
