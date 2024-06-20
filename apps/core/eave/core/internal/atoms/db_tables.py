from dataclasses import dataclass
from typing import ClassVar

from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.collectors.core.datastructures import DatabaseOperation, HttpRequestMethod
from eave.core.internal.atoms.db_record_fields import (
    CurrentPageRecordField,
    DeviceRecordField,
    GeoRecordField,
    MultiScalarTypeKeyValueRecordField,
    SessionRecordField,
    SingleScalarTypeKeyValueRecordField,
    TargetRecordField,
    TrafficSourceRecordField,
    UserRecordField,
)
from eave.core.internal.atoms.shared import BigQueryFieldMode


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


@dataclass(kw_only=True, frozen=True)
class BigQueryTableDefinition:
    table_id: str
    """The BigQuery table ID"""

    friendly_name: str
    """Friendly name for BigQuery table metadata"""

    description: str
    """Description for BigQuery table metadata"""

    schema: tuple[SchemaField, ...]
    """Table schema. This is authoritative."""


@dataclass(kw_only=True)
class BrowserEventAtom:
    TABLE_DEF: ClassVar[BigQueryTableDefinition] = BigQueryTableDefinition(
        table_id="atoms_browser_events",
        friendly_name="Browser Atoms",
        description="Browser atoms",
        schema=(
            SchemaField(
                name="action",
                description="The user action that caused this event.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SessionRecordField.schema(),
            UserRecordField.schema(),
            TrafficSourceRecordField.schema(),
            TargetRecordField.schema(),
            CurrentPageRecordField.schema(),
            DeviceRecordField.schema(),
            GeoRecordField.schema(),
            MultiScalarTypeKeyValueRecordField.schema(
                name="extra",
                description="Arbitrary event-specific parameters.",
            ),
            SchemaField(
                name="client_ip",
                description="The user's IP address.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            common_event_timestamp_field(),
            common_bq_insert_timestamp_field(),
        ),
    )

    action: str | None
    session: SessionRecordField | None
    user: UserRecordField | None
    traffic_source: TrafficSourceRecordField | None
    target: TargetRecordField | None
    current_page: CurrentPageRecordField | None
    device: DeviceRecordField | None
    geo: GeoRecordField | None
    extra: list[MultiScalarTypeKeyValueRecordField] | None
    client_ip: str | None
    timestamp: float | None


@dataclass(kw_only=True)
class DatabaseEventAtom:
    TABLE_DEF: ClassVar[BigQueryTableDefinition] = BigQueryTableDefinition(
        table_id="atoms_db_events",
        friendly_name="Database Atoms",
        description="Database atoms",
        schema=(
            SchemaField(
                name="operation",
                description="Which operation (SQL verb) was performed.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="db_name",
                description="The name of the database.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="table_name",
                description="The name of the table.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="statement",
                description="The full database statement.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            MultiScalarTypeKeyValueRecordField.schema(
                name="statement_values",
                description="The SQL parameter values passed into the statement.",
            ),
            SessionRecordField.schema(),
            UserRecordField.schema(),
            TrafficSourceRecordField.schema(),
            common_event_timestamp_field(),
            common_bq_insert_timestamp_field(),
        ),
    )

    operation: DatabaseOperation | None
    db_name: str | None
    table_name: str | None
    statement: str | None
    statement_values: list[MultiScalarTypeKeyValueRecordField] | None
    session: SessionRecordField | None
    user: UserRecordField | None
    traffic_source: TrafficSourceRecordField | None
    timestamp: float | None


@dataclass(kw_only=True)
class HttpClientEventAtom:
    TABLE_DEF: ClassVar[BigQueryTableDefinition] = BigQueryTableDefinition(
        table_id="atoms_http_client_events_v1",
        friendly_name="HTTP Client Atoms",
        description="HTTP Client atoms",
        schema=(
            SchemaField(
                name="request_method",
                description="Request method. eg: POST, GET",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="request_url",
                description="The requested URL.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SingleScalarTypeKeyValueRecordField[str].schema(
                name="request_headers",
                description="The headers for the outgoing request.",
                value_type=SqlTypeNames.STRING,
            ),
            SchemaField(
                name="request_payload",
                description="The JSON-encoded request body, if present.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SessionRecordField.schema(),
            UserRecordField.schema(),
            TrafficSourceRecordField.schema(),
            common_event_timestamp_field(),
            common_bq_insert_timestamp_field(),
        ),
    )

    request_method: HttpRequestMethod | None
    request_url: str | None
    request_headers: list[SingleScalarTypeKeyValueRecordField[str]] | None
    request_payload: str | None
    session: SessionRecordField | None
    user: UserRecordField | None
    traffic_source: TrafficSourceRecordField | None
    timestamp: float | None


@dataclass(kw_only=True)
class HttpServerEventAtom:
    TABLE_DEF: ClassVar[BigQueryTableDefinition] = BigQueryTableDefinition(
        table_id="atoms_http_server_events_v1",
        friendly_name="HTTP Server Atoms",
        description="HTTP Server atoms",
        schema=(
            SchemaField(
                name="request_method",
                description="Request method. eg: POST, GET",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="request_url",
                description="The requested URL.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SingleScalarTypeKeyValueRecordField[str].schema(
                name="request_headers",
                description="The headers for the incoming request.",
                value_type=SqlTypeNames.STRING,
            ),
            SchemaField(
                name="request_payload",
                description="The JSON-encoded request body, if present.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SessionRecordField.schema(),
            UserRecordField.schema(),
            TrafficSourceRecordField.schema(),
            common_event_timestamp_field(),
            common_bq_insert_timestamp_field(),
        ),
    )

    request_method: HttpRequestMethod | None
    request_url: str | None
    request_headers: list[SingleScalarTypeKeyValueRecordField[str]] | None
    request_payload: str | None
    session: SessionRecordField | None
    user: UserRecordField | None
    traffic_source: TrafficSourceRecordField | None
    timestamp: float | None
