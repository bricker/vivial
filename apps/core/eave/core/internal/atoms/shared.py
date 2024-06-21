import abc
from typing import Self
from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.core.internal.atoms.table_handle import BigQueryFieldMode


class Redactable(abc.ABC):
    @abc.abstractmethod
    def redact_sensitive_content(self) -> Self: ...


def common_bq_insert_timestamp_field() -> SchemaField:
    return SchemaField(
        name="__bq_insert_timestamp",
        description="When this record was inserted into BigQuery. This is an internal field and not reliable for exploring user journeys.",
        field_type=SqlTypeNames.TIMESTAMP,
        mode=BigQueryFieldMode.NULLABLE,
        default_value_expression="CURRENT_TIMESTAMP",
    )


def common_event_timestamp_field() -> SchemaField:
    return SchemaField(
        name="timestamp",
        description="When this event occurred.",
        field_type=SqlTypeNames.TIMESTAMP,
        mode=BigQueryFieldMode.NULLABLE,
    )
