from typing import Optional
import pydantic

from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel


class JiraInstallation(BaseResponseModel):
    """
    https://developer.atlassian.com/cloud/confluence/connect-app-descriptor/#lifecycle
    """
    id: pydantic.UUID4
    client_key: str
    base_url: str
    team_id: Optional[pydantic.UUID4]
    atlassian_actor_account_id: Optional[str]
    shared_secret: Optional[str]
    display_url: Optional[str]
    description: Optional[str]

class QueryJiraInstallationInput(BaseInputModel):
    client_key: str

class RegisterJiraInstallationInput(BaseInputModel):
    """
    These field names MUST match the field names defined in the ORM.
    It is recommended to not change these.
    """
    client_key: str
    base_url: str
    atlassian_actor_account_id: Optional[str]
    shared_secret: Optional[str]
    display_url: Optional[str]
    description: Optional[str]
