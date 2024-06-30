from eave.stdlib.core_api.models.virtual_event import BigQueryFieldMode
from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.core.internal.atoms.models.atom_types import (
    Atom,
    BrowserEventAtom,
    DatabaseEventAtom,
    HttpClientEventAtom,
    HttpServerEventAtom,
)
from eave.core.internal.atoms.models.db_record_fields import (
    CurrentPageRecordField,
    DeviceRecordField,
    GeoRecordField,
    MultiScalarTypeKeyValueRecordField,
    SingleScalarTypeKeyValueRecordField,
    TargetRecordField,
    UrlRecordField,
)

from ..base import BaseTestCase, assert_schemas_match


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
