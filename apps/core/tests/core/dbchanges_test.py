from eave.core.internal.bigquery import dbchanges
from .base import BaseTestCase

TABLE_NAME = "my_table"
BASIC_SELECT = f"SELECT id, name, age FROM {TABLE_NAME}"
BASIC_INSERT = f"INSERT INTO {TABLE_NAME} (name, age) VALUES ('tim', 3)"
NO_COLUMN_NAMES_INSERT = f"INSERT INTO {TABLE_NAME} VALUES ('tim', 3)"
BASIC_UPDATE = f"UPDATE {TABLE_NAME} SET name = 'tim', age = 34"
BASIC_DELETE = f"DELETE FROM {TABLE_NAME}"
WHERE_CLAUSE = "WHERE id > 12 AND name = 'allen'"
END_CLAUSE = ";"


class TestDatabaseChangeIngestion(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    def test_table_name_extraction(self):
        def check(s):
            assert dbchanges._table_name(s) == TABLE_NAME, f"wrong table name found in '{s}'"

        check(BASIC_SELECT + END_CLAUSE)
        check(BASIC_DELETE + END_CLAUSE)
        check(BASIC_INSERT + END_CLAUSE)
        check(BASIC_UPDATE + END_CLAUSE)
        check(NO_COLUMN_NAMES_INSERT + END_CLAUSE)
        check(f"{BASIC_SELECT} {WHERE_CLAUSE}{END_CLAUSE}")
        check(f"{BASIC_UPDATE} {WHERE_CLAUSE}{END_CLAUSE}")
        check(f"{BASIC_DELETE} {WHERE_CLAUSE}{END_CLAUSE}")

    def test_operation_name_extraction(self):
        def check(s, expected_op):
            assert dbchanges._operation_name(s) == expected_op, f"op {expected_op} not found in '{s}'"

        check(BASIC_SELECT + END_CLAUSE, "SELECT")
        check(BASIC_DELETE + END_CLAUSE, "DELETE")
        check(BASIC_INSERT + END_CLAUSE, "INSERT")
        check(BASIC_UPDATE + END_CLAUSE, "UPDATE")
        check(NO_COLUMN_NAMES_INSERT + END_CLAUSE, "INSERT")
        check(f"{BASIC_SELECT} {WHERE_CLAUSE}{END_CLAUSE}", "SELECT")
        check(f"{BASIC_UPDATE} {WHERE_CLAUSE}{END_CLAUSE}", "UPDATE")
        check(f"{BASIC_DELETE} {WHERE_CLAUSE}{END_CLAUSE}", "DELETE")

    def test_column_name_extraction(self):
        def check(s, expected_columns):
            assert (
                dbchanges._columns_from_statement(s) == expected_columns
            ), f"expected columns {expected_columns} not found in '{s}'"

        check(BASIC_SELECT + END_CLAUSE, [])
        check(BASIC_DELETE + END_CLAUSE, [])
        check(BASIC_INSERT + END_CLAUSE, ["name", "age"])
        # check(BASIC_UPDATE + END_CLAUSE, ["name", "age"])
        check(NO_COLUMN_NAMES_INSERT + END_CLAUSE, [])  # TODO: update
        check(f"{BASIC_SELECT} {WHERE_CLAUSE}{END_CLAUSE}", ["id", "name"])
        check(f"{BASIC_UPDATE} {WHERE_CLAUSE}{END_CLAUSE}", ["name", "age", "id", "name"])
        check(f"{BASIC_DELETE} {WHERE_CLAUSE}{END_CLAUSE}", ["id", "name"])
        # multi-operation statement
        check(f"{BASIC_INSERT}{END_CLAUSE} {BASIC_UPDATE} {WHERE_CLAUSE}{END_CLAUSE}", ["name", "age", "name", "age", "id", "name"])
        # multi-value per column name
        check(f"{BASIC_SELECT} WHERE Price BETWEEN 50 AND 60{END_CLAUSE}", ["Price"])
        # where is not end of statement
        check(f"{BASIC_SELECT} {WHERE_CLAUSE} ORDER BY name ASC LIMIT 10{END_CLAUSE}", ["id", "name"])
