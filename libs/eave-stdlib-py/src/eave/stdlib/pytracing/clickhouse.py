from typing import Any
import clickhouse_connect
import clickhouse_connect.driver.exceptions
from eave.stdlib.pytracing.datastructures import RawEvent
from eave.stdlib.util import compact_json

chclient = clickhouse_connect.get_client(host="localhost")


def insert(data: list[RawEvent]) -> None:
    chclient.insert(
        table="raw_events",
        column_names=[
            "team_id",
            "timestamp",
            "event_type",
            "event_params",
        ],
        data=[
            [
                d.team_id,
                d.timestamp,
                d.event_type,
                compact_json(d.event_params.__dict__),
            ]
            for d in data
        ],
        settings={
            "async_insert": 1,
            "wait_for_async_insert": 1,
        },
    )


def _json_serialize(v: Any) -> Any:
    if hasattr(v, "json_dict"):
        return v.json_dict
    elif hasattr(v, "__dict__"):
        return v.__dict__
    else:
        return v
