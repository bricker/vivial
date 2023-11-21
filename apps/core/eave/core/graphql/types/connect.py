import enum
from typing import Any, Optional
import uuid
import pydantic
import strawberry.federation as sb
from eave.core.internal.orm.connect_installation import ConnectInstallationOrm

from eave.stdlib.core_api.models import BaseInputModel, BaseResponseModel

@sb.enum
class AtlassianProduct(enum.StrEnum):
    jira = "jira"
    confluence = "confluence"


@sb.type
class ConnectInstallation:
    """
    https://developer.atlassian.com/cloud/confluence/connect-app-descriptor/#lifecycle
    """

    id: uuid.UUID = sb.field()
    product: AtlassianProduct = sb.field()
    client_key: str = sb.field()
    base_url: str = sb.field()
    org_url: str = sb.field()
    shared_secret: str = sb.field()
    team_id: Optional[uuid.UUID] = sb.field()
    atlassian_actor_account_id: Optional[str] = sb.field()
    display_url: Optional[str] = sb.field()
    description: Optional[str] = sb.field()

    @classmethod
    def from_orm(cls, orm: ConnectInstallationOrm) -> "ConnectInstallation":
        return ConnectInstallation(
            id=orm.id,
            product=AtlassianProduct(value=orm.product),
            client_key=orm.client_key,
            base_url=orm.base_url,
            org_url=orm.org_url or ConnectInstallationOrm.make_org_url(orm.base_url),
            shared_secret=orm.shared_secret,
            team_id=orm.team_id,
            atlassian_actor_account_id=orm.atlassian_actor_account_id,
            display_url=orm.display_url,
            description=orm.description,
        )

@sb.input
class QueryConnectInstallationInput:
    product: AtlassianProduct = sb.field()
    client_key: Optional[str] = sb.field()
    team_id: Optional[uuid.UUID | str] = sb.field()


@sb.input
class RegisterConnectInstallationInput:
    """
    These field names MUST match the field names defined in the ORM.
    It is recommended to not change these.
    """

    client_key: str = sb.field()
    product: AtlassianProduct = sb.field()
    base_url: str = sb.field()
    shared_secret: str = sb.field()
    atlassian_actor_account_id: Optional[str] = sb.field()
    display_url: Optional[str] = sb.field()
    description: Optional[str] = sb.field()
