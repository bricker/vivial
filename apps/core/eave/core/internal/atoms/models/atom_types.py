from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.collectors.core.datastructures import DatabaseOperation
from eave.core.internal.atoms.models.db_record_fields import (
    AccountRecordField,
    BigQueryRecordMetadataRecordField,
    CurrentPageRecordField,
    DeviceRecordField,
    GeoRecordField,
    MultiScalarTypeKeyValueRecordField,
    OpenAIRequestPropertiesRecordField,
    SessionRecordField,
    SingleScalarTypeKeyValueRecordField,
    TargetRecordField,
    TrafficSourceRecordField,
    UrlRecordField,
)
from eave.core.internal.atoms.models.enums import BrowserAction, HttpRequestMethod
from eave.stdlib.core_api.models.virtual_event import BigQueryFieldMode
from eave.stdlib.deidentification import REDACTABLE


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
class Atom(ABC):
    """
    Common fields for all Atom types.
    """

    session: SessionRecordField | None
    traffic_source: TrafficSourceRecordField | None
    visitor_id: str | None
    timestamp: float | None
    event_id: str | None
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
                name="event_id",
                description="A unique ID per atom, assigned by Eave. This can be used to distinguish otherwise identical events.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            BigQueryRecordMetadataRecordField.schema(),
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
    action: BrowserAction | None
    device: DeviceRecordField | None
    geo: GeoRecordField | None
    client_ip: str | None


@dataclass(kw_only=True)
class OpenAIChatCompletionAtom(Atom):
    @staticmethod
    def table_def() -> BigQueryTableDefinition:
        return BigQueryTableDefinition(
            table_id="atoms_openai_chat_completions",
            friendly_name="OpenAI Chat Completion Atoms",
            description="OpenAI Chat Completion atoms",
            schema=(
                SchemaField(
                    name="completion_id",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="completion_system_fingerprint",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="completion_created_timestamp",
                    field_type=SqlTypeNames.TIMESTAMP,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="completion_user_id",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="service_tier",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="model",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="prompt_tokens",
                    field_type=SqlTypeNames.INTEGER,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="completion_tokens",
                    field_type=SqlTypeNames.INTEGER,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="total_tokens",
                    field_type=SqlTypeNames.INTEGER,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="input_cost_usd_cents",
                    field_type=SqlTypeNames.NUMERIC,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="output_cost_usd_cents",
                    field_type=SqlTypeNames.NUMERIC,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="total_cost_usd_cents",
                    field_type=SqlTypeNames.NUMERIC,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="code_location",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                OpenAIRequestPropertiesRecordField.schema(),
                *Atom.common_atom_schema_fields(),
            ),
        )

    completion_id: str | None
    completion_system_fingerprint: str | None
    completion_created_timestamp: float | None
    completion_user_id: str | None
    service_tier: str | None
    model: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    input_cost_usd_cents: float | None
    output_cost_usd_cents: float | None
    total_cost_usd_cents: float | None
    code_location: str | None
    openai_request: OpenAIRequestPropertiesRecordField | None


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
