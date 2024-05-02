from dataclasses import dataclass
from typing import Any, Literal, Self, Type, TypedDict
import aiohttp
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.headers import MIME_TYPE_JSON
from eave.stdlib.logging import LOGGER
from eave.stdlib.typing import JsonObject

from eave.core.internal.config import CORE_API_APP_CONFIG

# Aliases for readability in types
MetabaseGroupIdKey = str
MetabaseDatabaseIdKey = str
MetabaseDatabaseSchemaIdKey = str
MetabaseDatabaseTableIdKey = str

class MetabaseDatabase(TypedDict, total=False):
    id: int | None
    name: str | None
    description: str | None
    features: list[str] | None
    cache_field_values_schedule: str | None
    timezone: str | None
    metadata_sync_schedule: str | None
    settings: dict[str, Any] | None
    caveats: str | None
    auto_run_queries: bool | None
    refingerprint: bool | None
    is_full_sync: bool | None
    is_sample: bool | None
    is_on_demand: bool | None
    created_at: str | None
    updated_at: str | None
    cache_ttl: int | None
    engine: str | None
    details: dict[str, Any] | None
    schedules: Any | None # dict[str, dict[str, Any]] | None # Using Any to be safe because this field isn't documented.
    initial_sync_status: str | None

class MetabaseUserGroupMembership(TypedDict, total=False):
    id: int | None
    is_group_manager: bool | None

class MetabaseUser(TypedDict, total=False):
    id: int | None
    email: str | None
    first_name: str | None
    last_name: str | None
    common_name: str | None
    sso_source: str | None
    locale: str | None
    is_active: bool | None
    is_qbnewb: bool | None
    is_superuser: bool | None
    user_group_memberships: list[MetabaseUserGroupMembership] | None
    login_attributes: dict[str, Any] | None
    date_joined: str | None
    last_login: str | None
    updated_at: str | None

class MetabasePermissionsGroup(TypedDict, total=False):
    id: int | None
    name: str | None
    members: list[MetabaseUser] | None

class MetabaseDatabaseActionPermissions(TypedDict, total=False):
    native: str | None
    schemas: str | dict[MetabaseDatabaseSchemaIdKey, dict[MetabaseDatabaseTableIdKey, str | None] | str | None] | None

# This "functional syntax" is necessary because the "data-model" key isn't a valid Python identifier
MetabaseDatabasePermissions = TypedDict("MetabaseDatabasePermissions", {
    "details": str | None,
    "data": MetabaseDatabaseActionPermissions | None,
    "download": MetabaseDatabaseActionPermissions | None,
    "data-model": MetabaseDatabaseActionPermissions | None,
}, total=False)



class MetabasePermissionsGraph(TypedDict, total=False):
    """
        {
          "groups": {
            "1": {
              "1": { "data": { "schemas": "block" } },
              "2": { "data": { "schemas": "block" } },
              "5": { "data": { "schemas": "block" } },
              "6": { "data": { "schemas": "block" } }
            },
            "2": { // group ID
              "1": { // database ID
                "data": { "native": "write", "schemas": "all" },
                "download": { "native": "full", "schemas": "full" },
                "data-model": { "schemas": "all" },
                "details": "yes"
              },
              "2": {
                "data": { "native": "write", "schemas": "all" },
                "download": { "native": "full", "schemas": "full" },
                "data-model": { "schemas": "all" },
                "details": "yes"
              },
              "5": {
                "data": { "native": "write", "schemas": "all" },
                "download": { "native": "full", "schemas": "full" },
                "data-model": { "schemas": "all" },
                "details": "yes"
              },
              "6": {
                "data": { "native": "write", "schemas": "all" },
                "download": { "native": "full", "schemas": "full" },
                "data-model": { "schemas": "all" },
                "details": "yes"
              },
              "13371337": {
                "data": { "native": "write", "schemas": "all" },
                "download": { "native": "full", "schemas": "full" },
                "data-model": { "schemas": "all" },
                "details": "yes"
              }
            },
            "3": {
              "1": { "data": { "schemas": "block" } },
              "2": { "data": { "schemas": "block" } },
              "5": {
                "data": {
                  "schemas": {
                    "team_4b885eea03f6488b93b186e2eeff5e13": {
                      "22": "all",
                      "23": "all",
                      "25": "all",
                      "26": "all"
                    }
                  }
                },
                "download": {
                  "schemas": {
                    "team_4b885eea03f6488b93b186e2eeff5e13": {
                      "22": "limited",
                      "23": "limited",
                      "25": "limited",
                      "26": "limited"
                    }
                  }
                }
              },
              "6": { "data": { "schemas": "block" } }
            },
            "4": {
              "1": { "data": { "schemas": "block" } },
              "2": { "data": { "schemas": "block" } },
              "5": { "data": { "schemas": "all" } },
              "6": {
                "download": { "native": "limited", "schemas": "limited" },
                "data": { "schemas": "all" }
              }
            }
          },
          "revision": 18,
          "sandboxes": [],
          "impersonations": []
        }
    """

    groups: dict[MetabaseGroupIdKey, dict[MetabaseDatabaseIdKey, MetabaseDatabasePermissions | None] | None] | None
    revision: int | None
    sandboxes: Any | None # Field not documented, using Any to be safe
    impersonations: Any | None # Field not documented, using Any to be safe

class MetabaseDashboard(TypedDict, total=False):
    pass

class MetabaseApiClient:
    _base_url: str
    _admin_api_key: str

    @classmethod
    def get_authenticated_client(cls) -> Self:
        admin_api_key = CORE_API_APP_CONFIG.metabase_admin_api_key
        metabase_url = SHARED_CONFIG.eave_internal_metabase_base
        return cls(base_url=metabase_url, admin_api_key=admin_api_key)

    def __init__(self, base_url: str, admin_api_key: str) -> None:
        self._base_url = base_url
        self._admin_api_key = admin_api_key

    async def create_user(self, email: str, group_id: int) -> tuple[MetabaseUser | None, aiohttp.ClientResponse]:
        """
        https://www.metabase.com/docs/latest/api/user#post-apiuser
        """
        response = await self.request(
            path="/api/user",
            method="POST",
            response_type=MetabaseUser,
            json={
                "email": email,
                "user_group_memberships": [{
                    "id": group_id,
                    "is_group_manager": False,
                }]
            },
        )

        return response

    async def create_group(self, name: str) -> tuple[MetabasePermissionsGroup | None, aiohttp.ClientResponse]:
        """
        https://www.metabase.com/docs/latest/api/permissions#post-apipermissionsgroup
        """
        response = await self.request(
            path="/api/permissions/group",
            method="POST",
            response_type=MetabasePermissionsGroup,
            json={
                "name": name,
            },
        )

        return response

    async def add_user_to_group(self, group_id: int, user_id: int) -> tuple[list[MetabaseUser] | None, aiohttp.ClientResponse]:
        """
        https://www.metabase.com/docs/latest/api/permissions#post-apipermissionsmembership
        """
        response = await self.request(
            path="/api/permissions/membership",
            method="POST",
            response_type=None, # Because this one returns a list, we have to parse this response manually
            json={
                "group_id": group_id,
                "user_id": user_id,
                "is_group_manager": False,
            },
        )

        try:
            data = await response[1].json()
            resource = [MetabaseUser(**e) for e in data]
        except Exception as e:
            LOGGER.exception(e)
            resource = None

        return resource, response[1]

    async def get_permissions_graph(self) -> tuple[MetabasePermissionsGraph | None, aiohttp.ClientResponse]:
        """
        https://www.metabase.com/docs/latest/api/permissions#get-apipermissionsgraph
        """
        response = await self.request(
            path="/api/permissions/graph",
            method="GET",
            response_type=MetabasePermissionsGraph,
        )

        return response

    async def get_execution_permissions_graph(self) -> tuple[MetabasePermissionsGraph | None, aiohttp.ClientResponse]:
        """
        https://www.metabase.com/docs/latest/api/permissions#get-apipermissionsexecutiongraph
        """
        response = await self.request(
            path="/api/permissions/execution/graph",
            method="GET",
            response_type=MetabasePermissionsGraph,
        )

        return response

    async def update_permissions_graph(self, graph: MetabasePermissionsGraph) -> tuple[MetabasePermissionsGraph | None, aiohttp.ClientResponse]:
        """
        https://www.metabase.com/docs/latest/api/permissions#put-apipermissionsgraph
        """
        response = await self.request(
            path="/api/permissions/graph",
            method="PUT",
            response_type=MetabasePermissionsGraph,
            json=graph,
        )

        return response

    async def update_execution_permissions_graph(self, graph: MetabasePermissionsGraph) -> tuple[MetabasePermissionsGraph | None, aiohttp.ClientResponse]:
        """
        https://www.metabase.com/docs/latest/api/permissions#put-apipermissionsexecutiongraph
        """
        response = await self.request(
            path="/api/permissions/execution/graph",
            method="PUT",
            response_type=MetabasePermissionsGraph,
            json=graph,
        )

        return response

    async def create_database(self, name: str, description: str, engine: str, details: JsonObject) -> tuple[MetabaseDatabase | None, aiohttp.ClientResponse]:
        """
        https://www.metabase.com/docs/latest/api/database#post-apidatabase
        """
        response = await self.request(
            path="/api/database",
            method="POST",
            response_type=MetabaseDatabase,
            json={
                "name": name,
                "description": description,
                "engine": engine,
                "details": details,
            },
        )

        return response

    async def update_database(self, id: int, name: str | None = None, description: str | None = None, details: JsonObject | None = None) -> tuple[MetabaseDatabase | None, aiohttp.ClientResponse]:
        """
        https://www.metabase.com/docs/latest/api/database#put-apidatabaseid
        """
        response = await self.request(
            path=f"/api/database/{id}",
            method="PUT",
            response_type=MetabaseDatabase,
            json={
                "name": name,
                "description": description,
                "details": details,
            },
        )

        return response

    async def create_dashboard(self, name: str) -> tuple[MetabaseDashboard | None, aiohttp.ClientResponse]:
        """
        https://www.metabase.com/docs/latest/api/dashboard#post-apidashboard
        """
        response = await self.request(
            path="/api/dashboard",
            method="POST",
            response_type=MetabaseDashboard,
            json={
                "name": name,
            },
        )

        return response

    async def copy_dashboard(self, from_id: int, to_name: str) -> tuple[MetabaseDashboard | None, aiohttp.ClientResponse]:
        """
        https://www.metabase.com/docs/latest/api/dashboard#post-apidashboardfrom-dashboard-idcopy
        """
        response = await self.request(
            path=f"/api/dashboard/{from_id}/copy",
            method="POST",
            response_type=MetabaseDashboard,
            json={
                "name": to_name,
            },
        )

        return response

    async def request[T](self, path: str, method: Literal["POST", "GET", "PUT", "PATCH", "DELETE"], response_type: type[T] | None = None, json: Any | None = None) -> tuple[T | None, aiohttp.ClientResponse]:
        async with aiohttp.ClientSession() as session:
            response = await session.request(
                method=method,
                url=f"{self._base_url}{path}",
                headers={
                    "accept": MIME_TYPE_JSON,
                    "x-api-key": self._admin_api_key,
                },
                json=json,
            )

            try:
                response.raise_for_status()

                # Be sure to consume the body while the session is still open
                data = await response.json()

                if response_type:
                    resource = response_type(**data)
                else:
                    resource = None
            except Exception as e:
                LOGGER.exception(e)
                resource = None

        return resource, response
