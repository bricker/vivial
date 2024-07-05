from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.core.internal.atoms.models.atom_types import (
    Atom,
    BrowserEventAtom,
    DatabaseEventAtom,
    HttpClientEventAtom,
    HttpServerEventAtom,
    OpenAIChatCompletionAtom,
)
from eave.core.internal.atoms.models.db_record_fields import (
    AccountRecordField,
    BigQueryRecordMetadataRecordField,
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

from ..base import BaseTestCase, assert_schemas_match


class TestAtomCommonSchemaField(BaseTestCase):
    async def test_schema(self):
        assert_schemas_match(
            Atom.common_atom_schema_fields(),
            (
                SessionRecordField.schema(),
                AccountRecordField.schema(),
                TrafficSourceRecordField.schema(),
                SchemaField(
                    name="visitor_id",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="timestamp",
                    field_type=SqlTypeNames.TIMESTAMP,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="event_id",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                BigQueryRecordMetadataRecordField.schema(),
            ),
        )


class TestOpenAIChatCompletionAtom(BaseTestCase):
    async def test_schema(self):
        self.fail("TODO")
        assert OpenAIChatCompletionAtom.table_def().table_id == "atoms_openai_chat_completions"

        assert_schemas_match(
            OpenAIChatCompletionAtom.table_def().schema,
            (
                SchemaField(
                    name="action",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                TargetRecordField.schema(),
                CurrentPageRecordField.schema(),
                DeviceRecordField.schema(),
                GeoRecordField.schema(),
                MultiScalarTypeKeyValueRecordField.schema(
                    name="extra",
                    description=self.anystr(),
                ),
                SchemaField(
                    name="client_ip",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                *Atom.common_atom_schema_fields(),
            ),
        )


class TestBrowserEventAtom(BaseTestCase):
    async def test_schema(self):
        assert BrowserEventAtom.table_def().table_id == "atoms_browser_events"

        assert_schemas_match(
            BrowserEventAtom.table_def().schema,
            (
                SchemaField(
                    name="action",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                TargetRecordField.schema(),
                CurrentPageRecordField.schema(),
                DeviceRecordField.schema(),
                GeoRecordField.schema(),
                MultiScalarTypeKeyValueRecordField.schema(
                    name="extra",
                    description=self.anystr(),
                ),
                SchemaField(
                    name="client_ip",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                *Atom.common_atom_schema_fields(),
            ),
        )


class TestDatabaseEventAtom(BaseTestCase):
    async def test_schema(self):
        assert DatabaseEventAtom.table_def().table_id == "atoms_db_events"
        assert_schemas_match(
            DatabaseEventAtom.table_def().schema,
            (
                SchemaField(
                    name="operation",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="db_name",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="table_name",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="statement",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                MultiScalarTypeKeyValueRecordField.schema(
                    name="statement_values",
                    description=self.anystr(),
                ),
                *Atom.common_atom_schema_fields(),
            ),
        )


class TestHttpServerEventAtom(BaseTestCase):
    async def test_schema(self):
        assert HttpServerEventAtom.table_def().table_id == "atoms_http_server_events"
        assert_schemas_match(
            HttpServerEventAtom.table_def().schema,
            (
                SchemaField(
                    name="request_method",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                UrlRecordField.schema(name="request_url", description=self.anystr()),
                SingleScalarTypeKeyValueRecordField[str].schema(
                    name="request_headers",
                    description=self.anystr(),
                    value_type=SqlTypeNames.STRING,
                ),
                SchemaField(
                    name="request_payload",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                *Atom.common_atom_schema_fields(),
            ),
        )


class TestHttpClientEventAtom(BaseTestCase):
    async def test_schema(self):
        assert HttpClientEventAtom.table_def().table_id == "atoms_http_client_events"
        assert_schemas_match(
            HttpClientEventAtom.table_def().schema,
            (
                SchemaField(
                    name="request_method",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                UrlRecordField.schema(name="request_url", description=self.anystr()),
                SingleScalarTypeKeyValueRecordField[str].schema(
                    name="request_headers",
                    description=self.anystr(),
                    value_type=SqlTypeNames.STRING,
                ),
                SchemaField(
                    name="request_payload",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                *Atom.common_atom_schema_fields(),
            ),
        )
