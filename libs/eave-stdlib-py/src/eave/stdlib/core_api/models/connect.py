import enum
from typing import Optional
import pydantic

from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel

class AtlassianProduct(enum.StrEnum):
    jira = "jira"
    confluence = "confluence"

class ConnectInstallation(BaseResponseModel):
    """
    https://developer.atlassian.com/cloud/confluence/connect-app-descriptor/#lifecycle
    """
    id: pydantic.UUID4
    product: AtlassianProduct
    client_key: str
    base_url: str
    shared_secret: str
    team_id: Optional[pydantic.UUID4]
    atlassian_actor_account_id: Optional[str]
    display_url: Optional[str]
    description: Optional[str]

class QueryConnectInstallationInput(BaseInputModel):
    client_key: str
    product: AtlassianProduct

class RegisterConnectInstallationInput(BaseInputModel):
    """
    These field names MUST match the field names defined in the ORM.
    It is recommended to not change these.
    """
    client_key: str
    product: AtlassianProduct
    base_url: str
    shared_secret: str
    atlassian_actor_account_id: Optional[str]
    display_url: Optional[str]
    description: Optional[str]
