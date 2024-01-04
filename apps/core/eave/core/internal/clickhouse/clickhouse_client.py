from dataclasses import dataclass
import datetime
import json
import re
from textwrap import dedent
from typing import Any, Sequence, cast
from uuid import UUID
import clickhouse_connect
import clickhouse_connect.driver.exceptions
from eave.core.internal.config import CORE_API_APP_CONFIG
from eave.monitoring.datastructures import DatabaseChangeEventPayload, EventType, RawEvent

chclient = clickhouse_connect.get_client(
    host=CORE_API_APP_CONFIG.clickhouse_host,
    settings={
        "session_timezone": "UTC",
    },
)

async def create_database(name: str) -> None:
    chclient.command(f"CREATE DATABASE IF NOT EXISTS {name}")
