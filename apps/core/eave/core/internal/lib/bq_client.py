import json
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import google.api_core.exceptions
from google.cloud import bigquery
from google.cloud.bigquery.table import RowIterator
from google.oauth2 import service_account as _service_account

from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER, LogContext


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

    def get_and_sync_or_create_table(
        self,
        *,
        dataset_id: str,
        table_id: str,
        schema: tuple[bigquery.SchemaField, ...],
        ctx: LogContext,
    ) -> bigquery.Table:
        local_table = self._construct_table(dataset_id=dataset_id, table_id=table_id)

        # Manually adding schema instead of passing into the Table initializer because the initializer doesn't have a type for the schema param.
        local_table.schema = schema

        remote_table = self._bq_client.create_table(
            table=local_table,
            exists_ok=True,
        )

        local_table_flattened_schema_fields = sorted(_flattened_schema_fields(local_table.schema))
        remote_table_flattened_schema_fields = sorted(_flattened_schema_fields(remote_table.schema))

        if local_table_flattened_schema_fields != remote_table_flattened_schema_fields:
            LOGGER.info("Schema mismatch. Updating remote schema.", {"table_id": table_id}, ctx)

            # The schemas don't match. Update the server schema to match the client schema.
            remote_table.schema = local_table.schema

            try:
                remote_table = self._bq_client.update_table(
                    remote_table,
                    fields=["schema"],
                )
            except Exception as e:
                # This may happen if a field was removed.
                # That isn't supposed to happen, but in case it did (developer error),
                # then we shouldn't prevent the insert.
                if SHARED_CONFIG.is_production:
                    # Log, but do not raise.
                    LOGGER.exception(e, ctx)
                else:
                    # in non-prod envs, raise
                    raise

        return remote_table

    def get_or_create_view(self, *, dataset_id: str, view_id: str, description: str, view_query: str) -> bigquery.Table:
        table = self._construct_table(dataset_id=dataset_id, table_id=view_id)
        table.description = description
        table.view_query = view_query

        r = self._bq_client.create_table(
            table=table,
            exists_ok=True,
        )
        return r

    def append_rows(self, *, table: bigquery.Table, rows: Sequence[Mapping[str, Any]]) -> Sequence[dict[str, Any]]:
        errors = self._bq_client.insert_rows(
            table=table,
            rows=rows,
            ignore_unknown_values=True,  # do not error if any row contains unknown values
            skip_invalid_rows=True,  # do not error if any row is invalid
        )

        return errors

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


def _flattened_schema_fields(fields: Iterable[bigquery.SchemaField]) -> list[str]:
    flattened_fields: list[str] = []
    for field in fields:
        flattened_fields.append(field.name)

        # Check for truthiness because the field.fields documentation says it's Optional, even though the typing doesn't reflect that.
        if field.fields and len(field.fields) > 0:
            flattened_fields.extend(_flattened_schema_fields(field.fields))

    return flattened_fields


def _field_names(fields: list[bigquery.SchemaField]) -> list[str]:
    return [f.name for f in fields]


EAVE_INTERNAL_BIGQUERY_ATOMS_DATASET_ID = "eave_atoms"
EAVE_INTERNAL_BIGQUERY_CLIENT = BigQueryClient()
