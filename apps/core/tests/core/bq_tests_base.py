from google.cloud import bigquery

from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.core.internal.orm.team import TeamOrm, bq_dataset_id
from eave.stdlib.config import SHARED_CONFIG

from .base import BaseTestCase


class BigQueryTestsBase(BaseTestCase):
    bq_client: bigquery.Client
    eave_team: TeamOrm
    client_credentials: ClientCredentialsOrm

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        async with self.db_session.begin() as s:
            self.eave_team = await self.make_team(session=s)
            self.client_credentials = await ClientCredentialsOrm.create(
                session=s,
                team_id=self.eave_team.id,
                description=self.anystr(),
                scope=ClientScope.write,
            )

        self.bq_client = bigquery.Client(project=SHARED_CONFIG.google_cloud_project)

        self.bq_client.delete_dataset(
            dataset=bq_dataset_id(self.eave_team.id),
            delete_contents=True,
            not_found_ok=True,
        )

    async def asyncTearDown(self) -> None:
        await super().asyncTearDown()

        self.bq_client.delete_dataset(
            dataset=bq_dataset_id(self.eave_team.id),
            delete_contents=True,
            not_found_ok=True,
        )

    def get_team_bq_dataset(self) -> bigquery.Dataset | None:
        try:
            dataset = self.bq_client.get_dataset(dataset_ref=bq_dataset_id(self.eave_team.id))
            return dataset
        except Exception as e:
            print(f"Google Cloud Error: {e}")
            return None

    def team_bq_dataset_exists(self) -> bool:
        dataset = self.get_team_bq_dataset()
        return dataset is not None

    def get_team_bq_table(self, table_name: str) -> bigquery.Table | None:
        table = EAVE_INTERNAL_BIGQUERY_CLIENT.get_table_or_none(
            dataset_id=bq_dataset_id(self.eave_team.id), table_id=table_name
        )
        return table

    def team_bq_table_exists(self, table_name: str) -> bool:
        table = self.get_team_bq_table(table_name)
        return table is not None
