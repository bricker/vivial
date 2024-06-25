from google.cloud.bigquery import SchemaField, SqlTypeNames
from eave.core.internal.atoms.atom_types import Atom, BrowserEventAtom, DatabaseEventAtom, HttpClientEventAtom, HttpServerEventAtom
from eave.core.internal.atoms.db_record_fields import CurrentPageRecordField, DeviceRecordField, GeoRecordField, MultiScalarTypeKeyValueRecordField, SingleScalarTypeKeyValueRecordField, TargetRecordField
from eave.core.internal.atoms.shared import BigQueryFieldMode
from ..base import BaseTestCase, assert_schemas_match


class TestBrowserEventAtom(BaseTestCase):
    async def test_schema(self):
        assert BrowserEventAtom.TABLE_DEF.table_id == "atoms_browser_events"

        assert_schemas_match(
            BrowserEventAtom.TABLE_DEF.schema,
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
        assert DatabaseEventAtom.TABLE_DEF.table_id == "atoms_db_events"
        assert_schemas_match(
            DatabaseEventAtom.TABLE_DEF.schema,
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
        assert HttpServerEventAtom.TABLE_DEF.table_id == "atoms_http_server_events"
        assert_schemas_match(
            HttpServerEventAtom.TABLE_DEF.schema,
            (
                SchemaField(
                    name="request_method",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="request_url",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
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

class TestHttpClickEventAtom(BaseTestCase):
    async def test_schema(self):
        assert HttpClientEventAtom.TABLE_DEF.table_id == "atoms_http_server_events"
        assert_schemas_match(
            HttpClientEventAtom.TABLE_DEF.schema,
            (
                SchemaField(
                    name="request_method",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="request_url",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
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
