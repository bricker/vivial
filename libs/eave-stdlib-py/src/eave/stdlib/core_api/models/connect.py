import enum
from typing import Any, Optional
import uuid
import pydantic

from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel


class AtlassianProduct(enum.StrEnum):
    jira = "jira"
    confluence = "confluence"


class ConnectInstallation(BaseResponseModel):
    """
    https://developer.atlassian.com/cloud/confluence/connect-app-descriptor/#lifecycle
    """

    id: uuid.UUID
    product: AtlassianProduct
    client_key: str
    base_url: str
    org_url: str
    shared_secret: str
    team_id: Optional[uuid.UUID]
    atlassian_actor_account_id: Optional[str]
    display_url: Optional[str]
    description: Optional[str]

class ConnectInstallationPeek(BaseResponseModel):
    """
    Connect Installation object with just basic info,
    intended for use when building a user interface and you
    don't need the full auth details.
    """
    id: uuid.UUID
    product: AtlassianProduct
    base_url: str
    org_url: str
    team_id: Optional[uuid.UUID]
    display_url: Optional[str]
    description: Optional[str]

class QueryConnectInstallationInput(BaseInputModel):
    product: AtlassianProduct
    client_key: Optional[str]
    team_id: Optional[uuid.UUID | str]

    @pydantic.root_validator(pre=True)
    def validate_sparse_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        client_key = values.get("client_key")
        team_id = values.get("team_id")
        assert client_key or team_id, "At least one of client_key or team_id must be specified"
        return values

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
