from eave.stdlib.exceptions import UnexpectedMissingValue
from eave.stdlib.test_util import UtilityBaseTestCase
import eave.stdlib.util

mut = eave.stdlib.util


class StdlibUtilTest(UtilityBaseTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()

    async def test_ensure_bytes(self):
        string = self.anystring()
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
        with self.assertRaises(UnexpectedMissingValue):
            mut.unwrap(None)

        v = self.anystring()
        assert mut.unwrap(None, v) == v
        assert mut.unwrap(v) == v

    async def test_redact(self):
        assert mut.redact(None) is None
        assert mut.redact(self.anystring()[:8]) == "(redacted)"
        assert mut.redact(self.anystring()[:2]) == "(redacted)"
        assert mut.redact(f"123456-{self.anystring()}-654321") == "1234..(redacted)..4321"
