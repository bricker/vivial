from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from google.cloud.bigquery import Dataset, DatasetReference, SchemaField, Table, TableReference

from eave.core.internal.orm.team import TeamOrm, bq_dataset_id
from eave.stdlib.logging import LogContext
from eave.stdlib.typing import JsonObject

from ..lib import bq_client


class BigQueryFieldMode(StrEnum):
    REQUIRED = "REQUIRED"
    NULLABLE = "NULLABLE"
    REPEATED = "REPEATED"


@dataclass(frozen=True)
class BigQueryTableDefinition:
    table_id: str
    schema: tuple[SchemaField, ...]
    friendly_name: str
    description: str

class BigQueryTableHandle:
    dataset_id: str
    table_def: BigQueryTableDefinition
    team: TeamOrm
    _bq_client: bq_client.BigQueryClient

    def __init__(self, *, team: TeamOrm) -> None:
        """
        If service_account is None, application default credentials will be used.
        """
        self._bq_client = bq_client.EAVE_INTERNAL_BIGQUERY_CLIENT
        self.team = team
        self.dataset_id = bq_dataset_id(team.id)
        self.bq_table = self.construct_bq_table()

    def construct_bq_table(self) -> Table:
        # Although the returned Table is always the same,
        # I've chosen to make this a separate function instead of a static instance property
        # because the returned Table is mutable.

        table = self._bq_client.construct_table(dataset_id=self.dataset_id, table_id=self.table_def.table_id)
        table.description = self.table_def.description
        table.friendly_name = self.table_def.friendly_name
        table.schema = self.table_def.schema
        return table
