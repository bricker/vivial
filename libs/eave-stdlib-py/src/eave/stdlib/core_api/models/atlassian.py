import uuid
from typing import List, Optional
from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel


class ConfluenceSpace(BaseResponseModel):
    key: str
    name: str


class AtlassianInstallation(BaseResponseModel):
    id: uuid.UUID
    team_id: uuid.UUID
    """eave TeamOrm model id"""
    atlassian_cloud_id: str
    confluence_space_key: Optional[str] = None
    "DEPRECATED: Always None"
    available_confluence_spaces: Optional[List[ConfluenceSpace]]


AtlassianInstallationPeek = AtlassianInstallation
"""Type Alias for naming consistency with other integrations"""


class AtlassianInstallationInput(BaseInputModel):
    atlassian_cloud_id: str
