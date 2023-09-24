import enum
from typing import Any, Optional, Self
import uuid
import pydantic

from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel
from eave.stdlib.model_validators import validate_at_least_one_of


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
    client_key: Optional[str] = None
    team_id: Optional[uuid.UUID | str] = None

    _v1 = validate_at_least_one_of("client_key", "team_id")

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
