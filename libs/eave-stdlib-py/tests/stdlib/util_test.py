import eave.stdlib.util

from .base import StdlibBaseTestCase

mut = eave.stdlib.util


class StdlibUtilTest(StdlibBaseTestCase):
    async def test_istr_eq(self):
        assert mut.istr_eq("A", "a")
        assert mut.istr_eq("a", "a")
        assert mut.istr_eq("A", "A")
        assert not mut.istr_eq("A", "b")

    async def test_sql_sanitized_identifier(self):
        assert mut.sql_sanitized_identifier("table_name`; drop tables; --") == "`table_name; drop tables; --`"
        assert mut.sql_sanitized_identifier("table_name```; drop tables; --") == "`table_name; drop tables; --`"
        assert mut.sql_sanitized_identifier("`table_name`; drop tables; --") == "`table_name; drop tables; --`"
        assert mut.sql_sanitized_identifier("`table_name; drop tables;` --`") == "`table_name; drop tables; --`"
        assert mut.sql_sanitized_identifier("`table_name\\; drop tables;` --`") == "`table_name; drop tables; --`"

    async def test_sql_sanitized_literal(self):
        assert mut.sql_sanitized_literal('table_name"; drop tables; --') == '"table_name; drop tables; --"'
        assert mut.sql_sanitized_literal("table_name'; drop tables; --") == '"table_name; drop tables; --"'
        assert (
            mut.sql_sanitized_literal('table_name"; drop tables; --', quotechar="'") == "'table_name; drop tables; --'"
        )
        assert (
            mut.sql_sanitized_literal("table_name'; drop tables; --", quotechar="'") == "'table_name; drop tables; --'"
        )
        assert (
            mut.sql_sanitized_literal("table_name\\'; drop tables; --", quotechar="'")
            == "'table_name; drop tables; --'"
        )

    async def test_tableize(self):
        assert mut.tableize("Account") == "account"
        assert mut.tableize("Github Installations") == "github_installations"
        assert mut.tableize("github_installations") == "github_installations"
        assert mut.tableize("Cohort 2023") == "cohort_2023"
        assert mut.tableize("--ab &&& c--") == "ab_c"
        assert mut.tableize('"; DROP TABLES') == "drop_tables"

    async def test_ensure_bytes(self):
        string = self.anystr()
        bytez = string.encode()
        assert mut.ensure_bytes(string) == bytez
        assert mut.ensure_bytes(bytez) == bytez

    async def test_ensure_uuid(self):
        uuid = self.anyuuid()

        assert mut.ensure_uuid(uuid) == uuid
        assert mut.ensure_uuid(uuid.int) == uuid
        assert mut.ensure_uuid(uuid.bytes) == uuid
        assert mut.ensure_uuid(uuid.hex) == uuid

    async def test_nand(self):
        assert mut.nand(False, False) is True
        assert mut.nand(True, False) is True
        assert mut.nand(False, True) is True
        assert mut.nand(True, True) is False

    async def test_nor(self):
        assert mut.nor(False, False) is True
        assert mut.nor(True, False) is False
        assert mut.nor(False, True) is False
        assert mut.nor(True, True) is False

    async def test_xor(self):
        assert mut.xor(False, False) is False
        assert mut.xor(True, False) is True
        assert mut.xor(False, True) is True
        assert mut.xor(True, True) is False

    async def test_xnor(self):
        assert mut.xnor(False, False) is True
        assert mut.xnor(True, False) is False
        assert mut.xnor(False, True) is False
        assert mut.xnor(True, True) is True

    async def test_unwrap(self):
        with self.assertRaises(mut.UnwrapError):
            mut.unwrap(None)

        v = self.anystr()
        assert mut.unwrap(None, v) == v
        assert mut.unwrap(v) == v

    async def test_redact(self):
        assert mut.redact(None) is None
        assert mut.redact(self.anystr()[:8]) == "[redacted 8 chars]"
        assert mut.redact(self.anystr()[:2]) == "[redacted 2 chars]"

        test_string = self.anystr()
        assert mut.redact(f"1234{test_string}4321") == f"1234[redacted {len(test_string)} chars]4321"

    async def test_num_suffix(self):
        assert mut.num_with_english_suffix(0) == "0th"
        assert mut.num_with_english_suffix(1) == "1st"
        assert mut.num_with_english_suffix(2) == "2nd"
        assert mut.num_with_english_suffix(3) == "3rd"
        assert mut.num_with_english_suffix(4) == "4th"
        assert mut.num_with_english_suffix(5) == "5th"
        assert mut.num_with_english_suffix(6) == "6th"
        assert mut.num_with_english_suffix(7) == "7th"
        assert mut.num_with_english_suffix(8) == "8th"
        assert mut.num_with_english_suffix(9) == "9th"
        assert mut.num_with_english_suffix(10) == "10th"
        assert mut.num_with_english_suffix(11) == "11th"
        assert mut.num_with_english_suffix(12) == "12th"
        assert mut.num_with_english_suffix(13) == "13th"
        assert mut.num_with_english_suffix(14) == "14th"
        assert mut.num_with_english_suffix(15) == "15th"
        assert mut.num_with_english_suffix(16) == "16th"
        assert mut.num_with_english_suffix(17) == "17th"
        assert mut.num_with_english_suffix(18) == "18th"
        assert mut.num_with_english_suffix(19) == "19th"
        assert mut.num_with_english_suffix(20) == "20th"
        assert mut.num_with_english_suffix(21) == "21st"
        assert mut.num_with_english_suffix(22) == "22nd"
        assert mut.num_with_english_suffix(23) == "23rd"
        assert mut.num_with_english_suffix(100) == "100th"
        assert mut.num_with_english_suffix(111) == "111th"
        assert mut.num_with_english_suffix(121) == "121st"
