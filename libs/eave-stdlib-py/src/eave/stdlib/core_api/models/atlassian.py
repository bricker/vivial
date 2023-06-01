import pydantic
from typing import List, Optional
from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel


class ConfluenceSpace(BaseResponseModel):
    key: str
    name: str


class AtlassianInstallation(BaseResponseModel):
    id: pydantic.UUID4
    team_id: pydantic.UUID4
    """eave TeamOrm model id"""
    atlassian_cloud_id: str
    confluence_space_key: Optional[str]
    available_confluence_spaces: Optional[List[ConfluenceSpace]]
    oauth_token_encoded: str


class AtlassianInstallationInput(BaseInputModel):
    atlassian_cloud_id: str