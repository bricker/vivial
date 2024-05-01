import threading
import unittest

"""
read from cookeis sets all vlues
write cookies only sets context values
"""


class ThreadedCorrelationContextTest(unittest.IsolatedAsyncioTestCase):
    async def test_values_can_be_written_and_read(self) -> None:
        from eave.collectors.core.correlation_context import ThreadedCorrelationContext

        ctx = ThreadedCorrelationContext()
        assert ctx.get("key") is None, "Initial value was not None"
        ctx.set("key", 1)
        assert ctx.get("key") == 1, "Set value was not read"
        ctx.set("key", 2)
        assert ctx.get("key") == 2, "Set value was not overwritten"
        assert ctx.to_json() == '{"_eave_context": {"key": 2}}', "Value was not set in dedicated context dict"

    async def test_empty_state(self) -> None:
        from eave.collectors.core.correlation_context import ThreadedCorrelationContext

        ctx = ThreadedCorrelationContext()
        assert ctx.get("key") is None, "Non-existent key value was not None"
        assert ctx.to_json() == '{"_eave_context": {}}', "Empty/default context didnt convert to json as expected"

    async def test_separate_async_thread_ctx_cannot_access_each_others_data(self) -> None:
        def _helper(keys) -> None:
            from eave.collectors.core.correlation_context import ThreadedCorrelationContext

            ctx = ThreadedCorrelationContext()
            for key in keys:
                ctx.set(key, 1)

            expected = '{"_eave_context": {' + ", ".join([f'"{k}": 1' for k in keys]) + "}}"
            assert ctx.to_json() == expected, "Context did not match expected content"

        t1 = threading.Thread(target=_helper, args=(["k1", "k2", "k3"],))
        t2 = threading.Thread(target=_helper, args=(["k4", "k5", "k6"],))
        t1.start()
        t2.start()

        t1.join()
        t2.join()

    async def test_child_threads_inherit_parent_ctx_values(self) -> None:
        from eave.collectors.core.correlation_context import ThreadedCorrelationContext

        ctx = ThreadedCorrelationContext()
        # given values exist in parent context
        ctx.set("parent", 0)

        def f1() -> None:
            assert ctx.get("parent") == 0, "Parent value not present in child thread t1"
            ctx.set("t1", 1)

        def f2() -> None:
            assert ctx.get("parent") == 0, "Parent value not present in child thread t2"
            ctx.set("t2", 2)

        t1 = threading.Thread(target=f1)
        t2 = threading.Thread(target=f2)
        t1.start()
        t2.start()

        t1.join()
        t2.join()

        assert ctx.to_json() == '{"_eave_context": {"parent": 0, "t1": 1, "t2": 2}}', "Values set by child threads not found"
