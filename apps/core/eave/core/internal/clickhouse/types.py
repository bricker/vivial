
from dataclasses import dataclass
from textwrap import dedent
from uuid import UUID

from clickhouse_connect.datatypes.base import ClickHouseType
from clickhouse_connect.driver.ddl import TableColumnDef

from eave.core.internal.clickhouse import clickhouse_client
from eave.monitoring.datastructures import RawEvent


@dataclass
class ClickHouseDatabase:
    name: str

@dataclass
class ClickHouseTableDefinition:
    name: str
    columns: list[TableColumnDef]
    engine: str
    primary_key_columns: list[str]

    @property
    def column_names(self) -> list[str]:
        return [c.name for c in self.columns]

    @property
    def column_types(self) -> list[ClickHouseType]:
        return [c.ch_type for c in self.columns]

class ClickHouseTableHandle:
    table: ClickHouseTableDefinition

    def __init__(self, team_id: UUID) -> None:
        self.team_id = team_id

    @property
    def database(self) -> str:
        return self.team_id.hex

    async def create_table(self) -> None:
        pkey = ", ".join(self.table.primary_key_columns)
        columns = ", ".join(c.col_expr for c in self.table.columns)

        clickhouse_client.chclient.command(
            dedent(f"""
                CREATE TABLE IF NOT EXISTS {self.database}.{self.table.name}
                ({columns})
                ENGINE {self.table.engine}
                PRIMARY KEY ({pkey})
                """
            ).strip(),
            settings={
                "allow_experimental_object_type": 1,
            },
        )

    async def insert(self, events: list[str]) -> None:
        ...

    async def query(self, query: str) -> None:
        ...

