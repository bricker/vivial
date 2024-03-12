from typing import Any
from google.cloud import bigquery
from google.cloud.bigquery.table import RowIterator
import google.api_core.exceptions
from eave.stdlib.config import SHARED_CONFIG

_bq_client = bigquery.Client(project=SHARED_CONFIG.google_cloud_project)


def create_dataset(*, dataset_name: str) -> None:
    dataset = bigquery.Dataset(f"{SHARED_CONFIG.google_cloud_project}.{dataset_name}")
    _bq_client.create_dataset(
        dataset=dataset,
        exists_ok=True,
    )


def create_table(*, dataset_name: str, table_name: str, schema: list[bigquery.SchemaField]):
    table = bigquery.Table(f"{SHARED_CONFIG.google_cloud_project}.{dataset_name}.{table_name}", schema=schema)
    _bq_client.create_table(
        table=table,
        exists_ok=True,
    )


def create_view(*, dataset_name: str, view_name: str, view_query: str):
    table = bigquery.Table(f"{SHARED_CONFIG.google_cloud_project}.{dataset_name}.{view_name}")
    table.view_query = view_query
    _bq_client.create_table(
        table=table,
        exists_ok=True,
    )


def append_rows(*, dataset_name: str, table_name: str, rows: list[dict[str, Any]], schema: list[bigquery.SchemaField]):
    table = bigquery.Table(f"{SHARED_CONFIG.google_cloud_project}.{dataset_name}.{table_name}")
    table.schema = schema

    _bq_client.insert_rows(table=table, selected_fields=schema, rows=rows)


def query(*, query: str) -> RowIterator:
    results = _bq_client.query_and_wait(
        query=query,
    )
    return results


def get_dataset(*, dataset_name: str) -> bigquery.Dataset | None:
    dataset = bigquery.DatasetReference(
        project=SHARED_CONFIG.google_cloud_project,
        dataset_id=dataset_name,
    )

    try:
        result = _bq_client.get_dataset(
            dataset_ref=dataset,
        )
        return result
    except google.api_core.exceptions.NotFound:
        return None


def get_table(*, dataset_name: str, table_name: str) -> bigquery.Table | None:
    table = bigquery.Table(f"{SHARED_CONFIG.google_cloud_project}.{dataset_name}.{table_name}")

    try:
        result = _bq_client.get_table(
            table=table,
        )

        return result
    except google.api_core.exceptions.NotFound:
        return None
