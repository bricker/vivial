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

@dataclass(frozen=True)
class BigQueryTableDefinition:
    table_id: str
    schema: list[SchemaField]

class BigQueryTableHandle:
    table_def: BigQueryTableDefinition
    team_id: UUID

    def __init__(self, *, team_id: UUID, service_account: str | None = None) -> None:
        """
        If service_account is None, application default credentials will be used.
        """
        self._bq_client = bq_client.BigQueryClient(service_account=service_account)
        self.team_id = team_id

    @property
    def dataset_id(self) -> str:
        return f"team_{self.team_id.hex}"

    async def insert(self, events: list[str]) -> None:
        ...
