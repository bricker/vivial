from google.cloud import bigquery

from eave.stdlib.config import SHARED_CONFIG
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.core.internal.orm.team import TeamOrm, bq_dataset_id
from tests.core.base import BaseTestCase

class BigQueryTestsBase(BaseTestCase):
    bq_client: bigquery.Client
    eave_team: TeamOrm

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        async with self.db_session.begin() as s:
            self.eave_team = await self.make_team(session=s)

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

    def bq_team_dataset_exists(self) -> bool:
        try:
            dataset = self.bq_client.get_dataset(dataset_ref=bq_dataset_id(self.eave_team.id))
        except Exception as e:
            print(f"Google Cloud Error: {e}")
            return False

        return dataset is not None

    def bq_table_exists(self, table_name: str) -> bool:
        table = EAVE_INTERNAL_BIGQUERY_CLIENT.get_table_or_none(
            dataset_id=bq_dataset_id(self.eave_team.id), table_id=table_name
        )
        return table is not None
