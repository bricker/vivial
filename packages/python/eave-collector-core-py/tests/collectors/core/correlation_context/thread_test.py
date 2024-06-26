import threading
import unittest

from eave.collectors.core.correlation_context import CORR_CTX, ThreadedCorrelationContext
from eave.collectors.core.correlation_context.base import EAVE_COLLECTOR_COOKIE_PREFIX


class ThreadedCorrelationContextTest(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self) -> None:
        super().tearDown()
        # manually reset private thread storage since asyncio tests are all launched from same thread
        CORR_CTX.clear()

    async def test_separate_async_thread_ctx_cannot_access_each_others_data(self) -> None:
        def _helper(keys) -> None:
            ctx = ThreadedCorrelationContext()
            for key in keys:
                ctx.set(key, "1")

            expected = "{" + ", ".join([f'"{k}": "1"' for k in keys]) + "}"
            assert ctx.to_json() == expected, "Context did not match expected content"

        t1 = threading.Thread(target=_helper, args=(["k1", "k2", "k3"],))
        t2 = threading.Thread(target=_helper, args=(["k4", "k5", "k6"],))
        t1.start()
        t2.start()

        t1.join()
        t2.join()

    async def test_child_threads_inherit_parent_ctx_values(self) -> None:
        self.fail("Not Implemented")

        ctx = ThreadedCorrelationContext()
        # given values exist in parent context
        ctx.set("parent", "0")

        def f1() -> None:
            assert ctx.get("parent") == "0", "Parent value not present in child thread t1"
            ctx.set("t1", "1")

        def f2() -> None:
            assert ctx.get("parent") == "0", "Parent value not present in child thread t2"
            ctx.set("t2", "2")

        t1 = threading.Thread(target=f1)
        t2 = threading.Thread(target=f2)
        t1.start()
        t2.start()

        t1.join()
        t2.join()

        assert ctx.to_json() == '{"parent": "0", "t1": "1", "t2": "2"}', "Values set by child threads not found"
