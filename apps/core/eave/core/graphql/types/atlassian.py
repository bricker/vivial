import uuid
from typing import List, Optional

import strawberry
from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel


@strawberry.type
class ConfluenceSpace:
    key: str
    name: str

@strawberry.type
class AtlassianInstallation:
    id: uuid.UUID
    team_id: uuid.UUID
    """eave TeamOrm model id"""
    atlassian_cloud_id: str
    confluence_space_key: Optional[str]
    "DEPRECATED: Always None"
    available_confluence_spaces: Optional[List[ConfluenceSpace]]


AtlassianInstallationPeek = AtlassianInstallation
"""Type Alias for naming consistency with other integrations"""

@strawberry.input
class AtlassianInstallationInput:
    atlassian_cloud_id: str
