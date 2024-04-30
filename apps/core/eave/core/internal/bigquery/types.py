from dataclasses import dataclass
from enum import StrEnum

from google.cloud.bigquery import SchemaField

from eave.core.internal.bigquery import bq_client
from eave.core.internal.orm.team import TeamOrm


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
    team: TeamOrm

    def __init__(self, *, team: TeamOrm) -> None:
        """
        If service_account is None, application default credentials will be used.
        """
        self._bq_client = bq_client.EAVE_INTERNAL_BIGQUERY_CLIENT
        self.team = team

    async def insert(self, events: list[str]) -> None:
        ...
