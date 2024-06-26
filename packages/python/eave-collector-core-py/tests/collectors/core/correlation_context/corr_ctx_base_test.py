import hashlib
import os
import unittest

from eave.collectors.core.correlation_context.base import EAVE_COLLECTOR_ACCOUNT_ID_ATTR_NAME, EAVE_COLLECTOR_COOKIE_PREFIX, EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX, EAVE_COLLECTOR_ENCRYPTED_COOKIE_PREFIX, BaseCorrelationContext, CorrCtxStorage, CorrelationContextAttr


class CorrelationContextAttrTest(unittest.IsolatedAsyncioTestCase):
    async def test_corr_context_attr_encryption(self) -> None:
        enc_key = hashlib.sha256(b"x").digest()

        original_attr = CorrelationContextAttr(
            key="key",
            value="value",
        )

        encrypted_attr = original_attr.to_encrypted(encryption_key=enc_key)
        assert encrypted_attr is not None

        decrypted_attr = CorrelationContextAttr.from_encrypted(decryption_key=enc_key, encrypted_value=encrypted_attr)
        assert decrypted_attr is not None
        assert decrypted_attr == original_attr

    async def test_corr_context_attr_encryption_invalid_key(self) -> None:
        attr = CorrelationContextAttr(
            key="key",
            value="value",
        )

        encrypted_attr = attr.to_encrypted(encryption_key=b"invalid")
        assert encrypted_attr is None

class CorrelationContextConstantsTest(unittest.IsolatedAsyncioTestCase):
    async def test_constants(self) -> None:
        # These can't change or other stuff will break (eg browser collector)
        assert EAVE_COLLECTOR_COOKIE_PREFIX == "_eave."
        assert EAVE_COLLECTOR_ENCRYPTED_COOKIE_PREFIX == "_eave.nc."
        assert EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX == "_eave.nc.act."
        assert EAVE_COLLECTOR_ACCOUNT_ID_ATTR_NAME == "account_id"

class CorrelationContextStorageTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        os.environ["EAVE_CREDENTIALS"] = "abc:123"
        await super().asyncSetUp()

    async def test_set_encrypted(self) -> None:
        ctx = CorrCtxStorage()
        assert len(ctx.updated) == 0

        ctx.set(prefix="x.", key="y", value="z", encrypted=True)
        assert len(ctx.updated) == 1
        assert ctx.get("x.y") is None

    async def test_set_not_encrypted(self) -> None:
        ctx = CorrCtxStorage()
        assert len(ctx.updated) == 0

        ctx.set(prefix="x.", key="y", value="z", encrypted=False)
        assert len(ctx.updated) == 1
        assert ctx.get("x.y") == "z"

    async def test_set_encrypted_invalid_creds(self) -> None:
        os.environ["EAVE_CREDENTIALS"] = "invalid"

        ctx = CorrCtxStorage()
        assert len(ctx.updated) == 0

        ctx.set(prefix="x.", key="y", value="z", encrypted=True)
        assert len(ctx.updated) == 0

    async def test_merged(self) -> None:
        ctx = CorrCtxStorage()
        ctx.received["x"] = "y"
        ctx.received["a"] = "b"
        ctx.updated["x"] = "z"
        ctx.updated["c"] = "d"

        assert ctx.merged() == {
            "a": "b",
            "x": "z",
            "c": "d",
        }

    async def test_updated_values_cookies(self) -> None:
        ctx = CorrCtxStorage()
        ctx.received["x"] = "y"
        ctx.updated["a"] = "b"
        ctx.updated["c"] = '"v"'
        assert ctx.updated_values_cookies() == ["a=b", "c=%22v%22"]

    async def test_load_from_cookies(self) -> None:
        ctx = CorrCtxStorage()

        cookies = {
            "other_cookie": "yummy",
            f"{EAVE_COLLECTOR_COOKIE_PREFIX}session_id": "ses",
            f"{EAVE_COLLECTOR_COOKIE_PREFIX}key": "value",
        }
        ctx.load_from_cookies(cookies)

        # non eave cookies should be skipped
        assert (
            ctx.to_json()
            == f'{{"{EAVE_COLLECTOR_COOKIE_PREFIX}session_id": "ses", "{EAVE_COLLECTOR_COOKIE_PREFIX}key": "value"}}'
        ), "Cookie conversion did not include only the expected cookies"

        # cookies should join join if existing ctx
        ctx.load_from_cookies(
            {f"{EAVE_COLLECTOR_COOKIE_PREFIX}visitor_id": "123", f"{EAVE_COLLECTOR_COOKIE_PREFIX}key": "new val"}
        )
        assert (
            ctx.to_json()
            == f'{{"{EAVE_COLLECTOR_COOKIE_PREFIX}session_id": "ses", "{EAVE_COLLECTOR_COOKIE_PREFIX}key": "new val", "{EAVE_COLLECTOR_COOKIE_PREFIX}visitor_id": "123"}}'
        ), "Context did not join as expected"


        ctx.load_from_cookies(cookies={"_eave.a": "b", "c": "d"})
        assert ctx.received == {
            "_eave.a": "b",
        }

class _ExampleCorrelationContext(BaseCorrelationContext):
    storage: CorrCtxStorage | None = None

    def init_storage(self) -> None:
        self.storage = CorrCtxStorage()

    def get_storage(self) -> CorrCtxStorage | None:
        if self.storage is None:
            self.init_storage()

        return self.storage

class BaseCorrelationContextTest(unittest.IsolatedAsyncioTestCase):
    def test_get(self) -> None:
        ctx = _ExampleCorrelationContext()
        assert ctx.get("x") is None

    def test_set_encrypted(self) -> None:
        ctx = _ExampleCorrelationContext()
        ctx.set("y", "z", prefix="a", encrypted=True)
        assert ctx.storage is not None
        assert len(ctx.storage.updated) == 1
        assert ctx.get("ay") is None # key was hashed

    def test_set_not_encrypted(self) -> None:
        ctx = _ExampleCorrelationContext()
        ctx.set("y", "z", prefix="a", encrypted=False)
        assert ctx.storage is not None
        assert len(ctx.storage.updated) == 1
        assert ctx.get("ay") == "z"

    def test_set_no_prefix(self) -> None:
        ctx = _ExampleCorrelationContext()
        ctx.set("y", "z", prefix=None, encrypted=False)
        assert ctx.storage is not None
        assert ctx.get("y") == "z"

    def test_to_dict(self) -> None:
        ctx = _ExampleCorrelationContext()
        assert len(ctx.to_dict()) == 0
        ctx.set(prefix="x", key="y", value="z")
        assert len(ctx.to_dict()) == 1

    def test_to_json(self) -> None:
        ctx = _ExampleCorrelationContext()
        assert ctx.to_json() == "{}"
        ctx.set(prefix="x", key="y", value="z")
        assert ctx.to_json() != "{}"

    def test_get_updated_values_cookies(self) -> None:
        ctx = _ExampleCorrelationContext()
        assert ctx.get_updated_values_cookies() == ""
        ctx.set(prefix="x", key="y", value="z")
        assert ctx.get_updated_values_cookies() != ""

    def test_from_cookies(self) -> None:
        ctx = _ExampleCorrelationContext()
        assert ctx.get("_eave.a") is None
        assert ctx.get("c") is None

        ctx.from_cookies(cookies={"_eave.a": "b", "c": "d"})
        assert ctx.get("_eave.a") == "b"
        assert ctx.get("c") is None

    def test_clear(self) -> None:
        ctx = _ExampleCorrelationContext()
        ctx.set(prefix="x", key="y", value="z")
        assert ctx.storage is not None
        assert len(ctx.storage.updated) == 1

        ctx.clear()
        assert len(ctx.storage.updated) == 0
