from typing import Any
from eave.stdlib.config import SHARED_CONFIG
import sqlalchemy.exc

from eave.core.internal.config import CORE_API_APP_CONFIG
import eave.core.internal.database as eave_db
from eave.core.internal.lib.metabase_api import MetabaseApiClient, MetabaseDatabase, MetabasePermissionsGroup
from eave.core.internal.orm.team import TeamOrm

from .base import BaseTestCase


class TestMetabasePermissionsManagement(BaseTestCase):
    _new_database: MetabaseDatabase | None = None
    _new_group: MetabasePermissionsGroup | None = None

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        self._metabase_api_client = MetabaseApiClient.get_authenticated_client()

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()

        # if self._new_database and (dbid := self._new_database.get("id")):
        #     await self._metabase_api_client.request(
        #         path=f"/api/database/{dbid}",
        #         method="DELETE",
        #     )

        # if self._new_group and (grid := self._new_group.get("id")):
        #     await self._metabase_api_client.request(
        #         path=f"/api/permissions/group/{grid}",
        #         method="DELETE",
        #     )

    async def test_metabase_permissions_management(self) -> None:
        async with self.db_session.begin() as s:
            eave_team = await self.make_team(s)


        new_database, _ = await self._metabase_api_client.create_database(
            name="-",
            description="",
            engine="bigquery-cloud-sdk",
            details={
                "project-id": "eave-staging", # SHARED_CONFIG.google_cloud_project, # FIXME
                "service-account-json": CORE_API_APP_CONFIG.metabase_ui_bigquery_accessor_gsa_key_json_str,
                "dataset-filters-type": "inclusion",
                "dataset-filters-patterns": "empty",
                "advanced-options": True,
                "use-jvm-timezone": False,
                "include-user-id-and-hash": False,
                "ssl": True,
            }
        )
        self._new_database = new_database

        new_group, _ = await self._metabase_api_client.create_group(name=f"{eave_team.name} ({eave_team.id.hex})")
        self._new_group = new_group

        if new_database and (new_database_id := new_database.get("id")) and new_group and (new_group_id := new_group.get("id")):
            permissions, _ = await self._metabase_api_client.get_permissions_graph()
            if permissions and (all_groups := permissions.get("groups")):
                for group_id, databases in all_groups.items():
                    if not databases:
                        continue

                    # 13371337 is a magic database ID for admins, I guess it means "all databases", it's internal to Metabase
                    if "13371337" in databases:
                        # This is the admin group, Metabase doesn't allow modifications.
                        continue

                    if group_id == str(new_group_id):
                        databases[str(new_database_id)] = {
                            "data": { "schemas": { eave_team.bq_dataset_id: "all" } },
                            "download": { "schemas": { eave_team.bq_dataset_id: "limited" } },
                        }
                    else:
                        # Block all other group's access to the new database
                        databases[str(new_database_id)] = {
                            "data": { "schemas": "block" },
                        }

                # await self._metabase_api_client.update_permissions_graph(graph=permissions)

            # await metabase_api_client.update_database(
            #     id=new_database_id,
            #     name=f"{eave_team.name}",
            #     description=f"Team ID: {eave_team.id.hex}",
            #     details={
            #         "project-id": SHARED_CONFIG.google_cloud_project,
            #         "service-account-json": CORE_API_APP_CONFIG.metabase_ui_bigquery_accessor_gsa_key_json_str,
            #         "dataset-filters-type": "inclusion",
            #         "dataset-filters-patterns": eave_team.bq_dataset_id,
            #         "advanced-options": True,
            #         "use-jvm-timezone": False,
            #         "include-user-id-and-hash": False,
            #         "ssl": True,
            #     }
            # )
