import threading
import unittest

from eave.collectors.core.correlation_context import ThreadedCorrelationContext
from eave.collectors.core.correlation_context.base import CONTEXT_NAME, COOKIE_PREFIX
from eave.collectors.core.correlation_context.thread import _local_thread_storage


class ThreadedCorrelationContextTest(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self) -> None:
        super().tearDown()
        # manually reset private thread storage since asyncio tests are all launched from same thread
        _local_thread_storage.eave = {}

    async def test_values_can_be_written_and_read(self) -> None:
        ctx = ThreadedCorrelationContext()
        assert ctx.get("key") is None, "Initial value was not None"
        ctx.set("key", 1)
        assert ctx.get("key") == 1, "Set value was not read"
        ctx.set("key", 2)
        assert ctx.get("key") == 2, "Set value was not overwritten"
        assert ctx.to_json() == '{"_eave_context": {"key": 2}}', "Value was not set in dedicated context dict"

    async def test_empty_state(self) -> None:
        ctx = ThreadedCorrelationContext()
        assert ctx.get("key") is None, "Non-existent key value was not None"
        assert ctx.to_json() == '{"_eave_context": {}}', "Empty/default context didnt convert to json as expected"

    async def test_separate_async_thread_ctx_cannot_access_each_others_data(self) -> None:
        def _helper(keys) -> None:
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

        assert (
            ctx.to_json() == '{"_eave_context": {"parent": 0, "t1": 1, "t2": 2}}'
        ), "Values set by child threads not found"

    async def test_initialize_from_cookies_performs_union(self) -> None:
        ctx = ThreadedCorrelationContext()
        cookies = {
            "other_cookie": "yummy",
            f"{COOKIE_PREFIX}session": "ses",
            CONTEXT_NAME: '{"key": "value", "other": "val"}',
        }
        ctx.from_cookies(cookies)

        # non eave cookies should be skipped
        assert (
            ctx.to_json() == '{"_eave_context": {"key": "value", "other": "val"}, "_eave_session": "ses"}'
        ), "Cookie conversion failed"

        # cookies should join join if existing ctx
        ctx.from_cookies({f"{COOKIE_PREFIX}visitor_id": "123", CONTEXT_NAME: '{"key": "new val", "key2": "val2"}'})
        assert (
            ctx.to_json()
            == '{"_eave_context": {"key": "new val", "other": "val", "key2": "val2"}, "_eave_session": "ses", "_eave_visitor_id": "123"}'
        ), "Context did not join as expected"

    async def test_convert_ctx_to_cookies_creates_valid_cookie(self) -> None:
        ctx = ThreadedCorrelationContext()
        cookies = {
            "other_cookie": "yummy",
            f"{COOKIE_PREFIX}session": "ses",
            CONTEXT_NAME: '{"key": "value", "other": "val"}',
        }
        ctx.from_cookies(cookies)

        assert (
            ctx.to_cookie() == "_eave_context=%7B%22key%22%3A+%22value%22%2C+%22other%22%3A+%22val%22%7D"
        ), "Context cookie was converted incorrectly"
