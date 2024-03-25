import json
from typing import Any, Mapping, Sequence
from google.cloud import bigquery
from google.oauth2 import service_account as _service_account
from google.cloud.bigquery.table import RowIterator
import google.api_core.exceptions


class BigQueryClient:
    _bq_client: bigquery.Client

    def __init__(self, service_account: str | None = None) -> None:
        if service_account:
            service_account_json = json.loads(service_account)
            credentials = _service_account.Credentials.from_service_account_info(service_account_json)
        else:
            credentials = None

        self._bq_client = bigquery.Client(credentials=credentials)

    def get_or_create_dataset(self, *, dataset_id: str) -> bigquery.Dataset:
        dataset = self._construct_dataset(dataset_id=dataset_id)

        r = self._bq_client.create_dataset(
            dataset=dataset,
            exists_ok=True,
        )
        return r

    def get_or_create_table(
        self, *, dataset_id: str, table_id: str, schema: list[bigquery.SchemaField]
    ) -> bigquery.Table:
        table = self._construct_table(dataset_id=dataset_id, table_id=table_id)
        table.schema = schema  # Doing this instead of passing into the initializer because the initializer doesn't have a type for the schema param.

        r = self._bq_client.create_table(
            table=table,
            exists_ok=True,
        )
        return r

    def get_or_create_view(self, *, dataset_id: str, view_id: str, view_query: str) -> bigquery.Table:
        table = self._construct_table(dataset_id=dataset_id, table_id=view_id)
        table.view_query = view_query

        r = self._bq_client.create_table(
            table=table,
            exists_ok=True,
        )
        return r

    def append_rows(self, *, table: bigquery.Table, rows: Sequence[Mapping[str, Any]]) -> None:
        self._bq_client.insert_rows(
            table=table,
            rows=rows,
            ignore_unknown_values=False,  # error if any row contains unknown values
            skip_invalid_rows=False,  # error if any row is invalid
        )

    def query(self, *, query: str) -> RowIterator:
        results = self._bq_client.query_and_wait(
            query=query,
        )
        return results

    def get_dataset_or_none(self, *, dataset_id: str) -> bigquery.Dataset | None:
        dataset_ref = self._construct_dataset_ref(dataset_id=dataset_id)

        try:
            result = self._bq_client.get_dataset(
                dataset_ref=dataset_ref,
            )
            return result
        except google.api_core.exceptions.NotFound:
            return None

    def get_table_or_none(self, *, dataset_id: str, table_id: str) -> bigquery.Table | None:
        try:
            result = self.get_table_or_exception(dataset_id=dataset_id, table_id=table_id)
            return result
        except google.api_core.exceptions.NotFound:
            return None

    def get_table_or_exception(self, *, dataset_id: str, table_id: str) -> bigquery.Table:
        table = self._construct_table(dataset_id=dataset_id, table_id=table_id)
        result = self._bq_client.get_table(table=table)
        return result

    def _construct_dataset_ref(self, *, dataset_id: str) -> bigquery.DatasetReference:
        dataset_ref = bigquery.DatasetReference(project=self._bq_client.project, dataset_id=dataset_id)
        return dataset_ref

    def _construct_table_ref(self, *, dataset_id: str, table_id: str) -> bigquery.TableReference:
        dataset_ref = self._construct_dataset_ref(dataset_id=dataset_id)
        table_ref = bigquery.TableReference(dataset_ref=dataset_ref, table_id=table_id)
        return table_ref

    def _construct_dataset(self, *, dataset_id: str) -> bigquery.Dataset:
        dataset_ref = self._construct_dataset_ref(dataset_id=dataset_id)
        dataset = bigquery.Dataset(dataset_ref=dataset_ref)
        return dataset

    def _construct_table(self, *, dataset_id: str, table_id: str) -> bigquery.Table:
        table_ref = self._construct_table_ref(dataset_id=dataset_id, table_id=table_id)
        table = bigquery.Table(table_ref=table_ref)
        return table


EAVE_INTERNAL_BIGQUERY_ATOMS_DATASET_ID = "eave_atoms"
EAVE_INTERNAL_BIGQUERY_CLIENT = BigQueryClient()
