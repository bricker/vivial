import threading

from eave.collectors.core.correlation_context import CORR_CTX, ThreadedCorrelationContext
from eave.collectors.core.correlation_context.base import EAVE_COLLECTOR_COOKIE_PREFIX

from ..base import BaseTestCase


class ThreadedCorrelationContextTest(BaseTestCase):
    async def asyncTearDown(self) -> None:
        super().tearDown()
        # manually reset private thread storage since asyncio tests are all launched from same thread
        CORR_CTX.clear()

    async def test_values_can_be_written_and_read(self) -> None:
        ctx = ThreadedCorrelationContext()
        assert ctx.get("key") is None, "Initial value was not None"
        ctx.set("key", "1", encrypt=False)
        assert ctx.get("key") == "1", "Set value was not read"
        ctx.set("key", "2", encrypt=False)
        assert ctx.get("key") == "2", "Set value was not overwritten"
        assert ctx.to_json() == '{"_eave.key": "2"}'

    async def test_empty_state(self) -> None:
        ctx = ThreadedCorrelationContext()
        assert ctx.get("key") is None, "Non-existent key value was not None"
        assert ctx.to_json() == "{}", "Empty/default context didnt convert to json as expected"

    async def test_separate_async_thread_ctx_cannot_access_each_others_data(self) -> None:
        def _helper(keys) -> None:
            ctx = ThreadedCorrelationContext()
            for key in keys:
                ctx.set(key, "1", encrypt=False)

            expected = "{" + ", ".join([f'"{EAVE_COLLECTOR_COOKIE_PREFIX}{k}": "1"' for k in keys]) + "}"
            assert ctx.to_json() == expected, "Context did not match expected content"

        t1 = threading.Thread(target=_helper, args=(["k1", "k2", "k3"],))
        t2 = threading.Thread(target=_helper, args=(["k4", "k5", "k6"],))
        t1.start()
        t2.start()

        t1.join()
        t2.join()

    async def test_child_threads_inherit_parent_ctx_values(self) -> None:
        self.skipTest("Not Implemented")

        ctx = ThreadedCorrelationContext()
        # given values exist in parent context
        ctx.set("parent", "0", encrypted=False)

        def f1() -> None:
            assert ctx.get("parent") == "0", "Parent value not present in child thread t1"
            ctx.set("t1", "1", encrypt=False)

        def f2() -> None:
            assert ctx.get("parent") == "0", "Parent value not present in child thread t2"
            ctx.set("t2", "2", encrypt=False)

        t1 = threading.Thread(target=f1)
        t2 = threading.Thread(target=f2)
        t1.start()
        t2.start()

        t1.join()
        t2.join()

        assert ctx.to_json() == '{"parent": "0", "t1": "1", "t2": "2"}', "Values set by child threads not found"

    async def test_convert_ctx_to_cookies_creates_valid_cookie(self) -> None:
        ctx = ThreadedCorrelationContext()
        ctx.set("session_id", "ses", encrypt=False)
        ctx.set("key", '"value"', encrypt=False)

        # expect URL encoded
        assert ctx.get_updated_values_cookies() == [
            f"{EAVE_COLLECTOR_COOKIE_PREFIX}session_id=ses; SameSite=Lax; Secure; Path=/",
            f"{EAVE_COLLECTOR_COOKIE_PREFIX}key=%22value%22; SameSite=Lax; Secure; Path=/",
        ], "Context cookie was converted incorrectly"
