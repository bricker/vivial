from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID
from google.cloud.bigquery import SchemaField

from eave.core.internal.bigquery import bq_client

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
    def dataset(self) -> str:
        return self.team_id.hex

    async def create_table(self) -> None:
        bq_client.create_table(
            dataset_name=self.dataset,
            table_name=self.table.name,
            schema=self.table.schema,
        )

    async def insert(self, events: list[str]) -> None:
        ...

    async def query(self, query: str) -> None:
        ...
