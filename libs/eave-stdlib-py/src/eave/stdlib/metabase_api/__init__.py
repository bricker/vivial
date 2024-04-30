from typing import Any, Literal, Self
import aiohttp
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.typing import JsonObject


class MetabaseApiClient:
    _base_url: str
    _api_key: str

    @classmethod
    def create(cls) -> Self:
        api_key = SHARED_CONFIG.metabase_admin_api_key
        metabase_url = SHARED_CONFIG.eave_public_metabase_base
        return cls(base_url=metabase_url, api_key=api_key)

    async def __init__(self, base_url: str, api_key: str) -> None:
        self._base_url = base_url
        self._api_key = api_key

    async def create_user(self, email: str, group_id: int) -> aiohttp.ClientResponse:
        """
        https://www.metabase.com/docs/latest/api/user#post-apiuser
        """
        response = await self.request(
            path="/api/user",
            method="POST",
            json={
                "email": email,
                "user_group_memberships": [{
                    "id": group_id,
                    "is_group_manager": False,
                }]
            },
        )

        return response

    async def create_group(self, name: str) -> aiohttp.ClientResponse:
        """
        https://www.metabase.com/docs/latest/api/permissions#post-apipermissionsgroup
        """
        response = await self.request(
            path="/api/permissions/group",
            method="POST",
            json={
                "name": name,
            },
        )

        return response

    async def add_user_to_group(self, group_id: int, user_id: int) -> aiohttp.ClientResponse:
        """
        https://www.metabase.com/docs/latest/api/permissions#post-apipermissionsmembership
        """
        response = await self.request(
            path="/api/permissions/membership",
            method="POST",
            json={
                "group_id": group_id,
                "user_id": user_id,
                "is_group_manager": False,
            },
        )

        return response

    async def get_permissions_graph(self) -> aiohttp.ClientResponse:
        """
        https://www.metabase.com/docs/latest/api/permissions#get-apipermissionsgraph
        """
        response = await self.request(
            path="/api/permissions/graph",
            method="GET",
        )

        return response

    async def get_execution_permissions_graph(self) -> aiohttp.ClientResponse:
        """
        https://www.metabase.com/docs/latest/api/permissions#get-apipermissionsexecutiongraph
        """
        response = await self.request(
            path="/api/permissions/execution/graph",
            method="GET",
        )

        return response

    async def update_permissions_graph(self, graph: JsonObject) -> aiohttp.ClientResponse:
        """
        https://www.metabase.com/docs/latest/api/permissions#put-apipermissionsgraph
        """
        response = await self.request(
            path="/api/permissions/graph",
            method="PUT",
            json={
                "body": graph,
            },
        )

        return response

    async def update_execution_permissions_graph(self, graph: JsonObject) -> aiohttp.ClientResponse:
        """
        https://www.metabase.com/docs/latest/api/permissions#put-apipermissionsexecutiongraph
        """
        response = await self.request(
            path="/api/permissions/execution/graph",
            method="PUT",
            json={
                "body": graph,
            },
        )

        return response

    async def create_database(self, name: str, engine: str, details: JsonObject) -> aiohttp.ClientResponse:
        """
        https://www.metabase.com/docs/latest/api/database#post-apidatabase
        """
        response = await self.request(
            path="/api/permissions/membership",
            method="POST",
            json={
                "name": name,
                "engine": engine,
                "details": details,
            },
        )

        return response

    async def create_dashboard(self, name: str) -> aiohttp.ClientResponse:
        """
        https://www.metabase.com/docs/latest/api/dashboard#post-apidashboard
        """
        response = await self.request(
            path="/api/dashboard",
            method="POST",
            json={
                "name": name,
            },
        )

        return response

    async def copy_dashboard(self, from_id: int, to_name: str) -> aiohttp.ClientResponse:
        """
        https://www.metabase.com/docs/latest/api/dashboard#post-apidashboardfrom-dashboard-idcopy
        """
        response = await self.request(
            path=f"/api/dashboard/{from_id}/copy",
            method="POST",
            json={
                "name": to_name,
            },
        )

        return response

    async def request(self, path: str, method: Literal["POST", "GET", "PUT", "PATCH", "DELETE"], json: JsonObject | None = None) -> aiohttp.ClientResponse:
        async with aiohttp.ClientSession() as session:
            response = await session.request(
                method=method,
                url=f"{self._base_url}{path}",
                headers={
                    "x-api-key": self._api_key,
                },
                json=json,
            )

            # Consume the body while the session is still open
            await response.read()

        return response
