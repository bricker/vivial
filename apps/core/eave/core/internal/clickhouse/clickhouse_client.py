import clickhouse_connect
import clickhouse_connect.driver.exceptions
from eave.core.internal.config import CORE_API_APP_CONFIG

chclient = clickhouse_connect.get_client(
    host=CORE_API_APP_CONFIG.clickhouse_host,
    settings={
        "session_timezone": "UTC",
    },
)


async def create_database(name: str) -> None:
    chclient.command(f"CREATE DATABASE IF NOT EXISTS {name}")
