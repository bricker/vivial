from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID
from google.cloud.bigquery import Dataset, SchemaField, Table
from google.cloud.bigquery.table import RowIterator

from eave.core.internal.bigquery import bq_client
from eave.stdlib.config import SHARED_CONFIG

class BigQueryFieldMode(StrEnum):
    REQUIRED = "REQUIRED"
    NULLABLE = "NULLABLE"
    REPEATED = "REPEATED"

@dataclass
class BigQueryTableDefinition:
    name: str
    schema: list[SchemaField]

class BigQueryTableHandle:
    table: BigQueryTableDefinition

    def __init__(self, team_id: UUID) -> None:
        self.team_id = team_id

    @property
    def dataset_name(self) -> str:
        return f"team_{self.team_id.hex}"

    def get_dataset(self) -> Dataset | None:
        dataset = bq_client.get_dataset(dataset_name=self.dataset_name)
        return dataset

    def get_table(self) -> Table | None:
        table = bq_client.get_table(dataset_name=self.dataset_name, table_name=self.table.name)
        return table

    async def insert(self, events: list[str]) -> None:
        ...

    async def query(self, query: str) -> RowIterator:
        ...
