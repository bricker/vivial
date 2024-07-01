from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.collectors.core.datastructures import DatabaseOperation, HttpRequestMethod
from eave.core.internal.atoms.models.db_record_fields import (
    AccountRecordField,
    CurrentPageRecordField,
    DeviceRecordField,
    GeoRecordField,
    MultiScalarTypeKeyValueRecordField,
    SessionRecordField,
    SingleScalarTypeKeyValueRecordField,
    TargetRecordField,
    TrafficSourceRecordField,
    UrlRecordField,
)
from eave.stdlib.core_api.models.virtual_event import BigQueryFieldMode
from eave.stdlib.deidentification import Redactable, REDACTABLE


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


@dataclass
class Atom(ABC, Redactable):
    """
    Common fields for all Atom types.
    """

    session: SessionRecordField | None
    traffic_source: TrafficSourceRecordField | None
    visitor_id: str | None
    timestamp: float | None
    account: AccountRecordField | None = field(metadata={REDACTABLE: True})

    @staticmethod
    @abstractmethod
    def table_def() -> BigQueryTableDefinition: ...

    @staticmethod
    def common_atom_schema_fields() -> tuple[SchemaField, ...]:
        return (
            SessionRecordField.schema(),
            AccountRecordField.schema(),
            TrafficSourceRecordField.schema(),
            SchemaField(
                name="visitor_id",
                description="A unique ID per device, assigned by Eave. This ID is persisted across sessions on the same device.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="timestamp",
                description="When this event occurred.",
                field_type=SqlTypeNames.TIMESTAMP,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="__bq_insert_timestamp",
                description="When this record was inserted into BigQuery. This is an internal field and not reliable for exploring user journeys.",
                field_type=SqlTypeNames.TIMESTAMP,
                mode=BigQueryFieldMode.NULLABLE,
                default_value_expression="CURRENT_TIMESTAMP",
            ),
        )


@dataclass(kw_only=True)
class BrowserEventAtom(Atom):
    @staticmethod
    def table_def() -> BigQueryTableDefinition:
        return BigQueryTableDefinition(
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
                *Atom.common_atom_schema_fields(),
            ),
        )

    target: TargetRecordField | None = field(metadata={REDACTABLE: True})
    current_page: CurrentPageRecordField | None = field(metadata={REDACTABLE: True})
    extra: list[MultiScalarTypeKeyValueRecordField] | None = field(metadata={REDACTABLE: True})
    action: str | None
    device: DeviceRecordField | None
    geo: GeoRecordField | None
    client_ip: str | None


@dataclass(kw_only=True)
class DatabaseEventAtom(Atom):
    @staticmethod
    def table_def() -> BigQueryTableDefinition:
        return BigQueryTableDefinition(
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
                *Atom.common_atom_schema_fields(),
            ),
        )

    operation: DatabaseOperation | None
    db_name: str | None
    table_name: str | None
    statement: str | None = field(metadata={REDACTABLE: True})
    statement_values: list[MultiScalarTypeKeyValueRecordField] | None = field(metadata={REDACTABLE: True})


@dataclass(kw_only=True)
class HttpClientEventAtom(Atom):
    @staticmethod
    def table_def() -> BigQueryTableDefinition:
        return BigQueryTableDefinition(
            table_id="atoms_http_client_events",
            friendly_name="HTTP Client Atoms",
            description="HTTP Client atoms",
            schema=(
                SchemaField(
                    name="request_method",
                    description="Request method. eg: POST, GET",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                UrlRecordField.schema(name="request_url", description="The requested URL."),
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
                *Atom.common_atom_schema_fields(),
            ),
        )

    request_method: HttpRequestMethod | None
    request_url: UrlRecordField | None = field(metadata={REDACTABLE: True})
    request_headers: list[SingleScalarTypeKeyValueRecordField[str]] | None = field(metadata={REDACTABLE: True})
    request_payload: str | None = field(metadata={REDACTABLE: True})


@dataclass(kw_only=True)
class HttpServerEventAtom(Atom):
    @staticmethod
    def table_def() -> BigQueryTableDefinition:
        return BigQueryTableDefinition(
            table_id="atoms_http_server_events",
            friendly_name="HTTP Server Atoms",
            description="HTTP Server atoms",
            schema=(
                SchemaField(
                    name="request_method",
                    description="Request method. eg: POST, GET",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                UrlRecordField.schema(name="request_url", description="The requested URL."),
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
                *Atom.common_atom_schema_fields(),
            ),
        )

    request_method: HttpRequestMethod | None
    request_url: UrlRecordField | None = field(metadata={REDACTABLE: True})
    request_headers: list[SingleScalarTypeKeyValueRecordField[str]] | None = field(metadata={REDACTABLE: True})
    request_payload: str | None = field(metadata={REDACTABLE: True})
