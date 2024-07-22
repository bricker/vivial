import datetime
import json
import pprint
from textwrap import dedent
from time import sleep
from typing import Any, cast
import uuid
from google.cloud import bigquery
import click

class _DatabaseTypesJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, uuid.UUID):
            return str(o)
        elif isinstance(o, datetime.datetime):
            return o.isoformat()
        else:
            super().default(o)

_bq_client = bigquery.Client()

_SLEEPSEC = 5

@click.command()
@click.option("-q", "--query", required=True)
def stream(*, query: str) -> None:
    last_insert_timestamp = (datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(minutes=30)).isoformat()

    i = 0
    z = 0
    while z < _SLEEPSEC*100:
        z += 1
        mquery = query.format(last_insert_timestamp=last_insert_timestamp)
        results = _bq_client.query_and_wait(
            query=mquery,
        )

        for result in results:
            i += 1
            result = cast(bigquery.Row, result)
            last_insert_timestamp = result.get("metadata_insert_timestamp").isoformat()

            j = json.dumps({"__ROW__": i, "__TS__": datetime.datetime.now().isoformat(), **{k: result.get(k) for k in result.keys()}}, cls=_DatabaseTypesJSONEncoder)
            print(j, flush=True)

        sleep(_SLEEPSEC)

if __name__ == "__main__":
    stream()