import re
from typing import Any
from google.cloud import bigquery
from google.cloud.bigquery_storage_v1.services.big_query_write import BigQueryWriteAsyncClient
from google.cloud.bigquery_storage_v1.types import AppendRowsRequest

from eave.stdlib.config import SHARED_CONFIG

bq_write_client = BigQueryWriteAsyncClient()
bq_mgmt_client = bigquery.Client(project=SHARED_CONFIG.google_cloud_project)

def create_dataset(*, dataset_name: str) -> None:
    dataset = bigquery.Dataset(f"{SHARED_CONFIG.google_cloud_project}.{dataset_name}")
    bq_mgmt_client.create_dataset(
        dataset=dataset,
        exists_ok=True,
    )

def create_table(*, dataset_name: str, table_name: str, schema: list[bigquery.SchemaField]):
    table = bigquery.Table(f"{SHARED_CONFIG.google_cloud_project}.{dataset_name}.{table_name}", schema=schema)
    bq_mgmt_client.create_table(
        table=table,
        exists_ok=True,
    )

def create_view(*, dataset_name: str, view_name: str, view_query: str):
    table = bigquery.Table(f"{SHARED_CONFIG.google_cloud_project}.{dataset_name}.{view_name}")
    table.view_query = view_query
    bq_mgmt_client.create_table(
        table=table,
        exists_ok=True,
    )

async def append_rows(*, dataset_name: str, table_name: str, rows: list[dict[str, Any]]):
    client = BigQueryWriteAsyncClient()

    request = AppendRowsRequest(
        write_stream="write_stream_value",
    )

    await client.append_rows(requests=request_generator())
