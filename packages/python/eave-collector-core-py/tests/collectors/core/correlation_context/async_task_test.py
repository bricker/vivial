import asyncio
import unittest

from eave.collectors.core.correlation_context import AsyncioCorrelationContext
from eave.collectors.core.correlation_context.base import EAVE_COLLECTOR_COOKIE_PREFIX


class AsyncioCorrelationContextTest(unittest.IsolatedAsyncioTestCase):
    async def test_values_can_be_written_and_read(self) -> None:
        ctx = AsyncioCorrelationContext()
        assert ctx.get("key") is None, "Initial value was not None"
        ctx.set("key", "1", encrypt=False)
        assert ctx.get("key") == "1", "Set value was not read"
        ctx.set("key", "2", encrypt=False)
        assert ctx.get("key") == "2", "Set value was not overwritten"
        assert ctx.to_json() == '{"_eave.key": "2"}'

    async def test_empty_state(self) -> None:
        ctx = AsyncioCorrelationContext()
        assert ctx.get("key") is None, "Non-existent key value was not None"
        assert ctx.to_json() == "{}", "Empty/default context didnt convert to json as expected"

    async def test_separate_async_task_ctx_cannot_access_each_others_data(self) -> None:
        async def _helper(keys) -> None:
            ctx = AsyncioCorrelationContext()
            for key in keys:
                ctx.set(key, "1", encrypt=False)

            expected = "{" + ", ".join([f'"_eave.{k}": "1"' for k in keys]) + "}"
            assert ctx.to_json() == expected, "Context contained other than expected values"

        t1 = asyncio.create_task(_helper(["k1", "k2", "k3"]))
        t2 = asyncio.create_task(_helper(["k4", "k5", "k6"]))
        await asyncio.gather(t1, t2)

    async def test_child_tasks_inherit_parent_ctx_values(self) -> None:
        ctx = AsyncioCorrelationContext()
        # given values exist in parent context
        ctx.set("parent", "0", encrypt=False)

        async def task1() -> None:
            assert ctx.get("parent") == "0", "Parent value not present in child task t1"
            ctx.set("t1", "1", encrypt=False)

        async def task2() -> None:
            assert ctx.get("parent") == "0", "Parent value not present in child task t2"
            ctx.set("t2", "2", encrypt=False)

        t1 = asyncio.create_task(task1())
        t2 = asyncio.create_task(task2())
        await asyncio.gather(t1, t2)

        assert ctx.to_json() == '{"_eave.parent": "0", "_eave.t1": "1", "_eave.t2": "2"}', "Values set by child tasks not found"

    async def test_initialize_from_cookies_performs_union(self) -> None:
        ctx = AsyncioCorrelationContext()
        cookies = {
            "other_cookie": "yummy",
            f"{EAVE_COLLECTOR_COOKIE_PREFIX}session_id": "ses",
            f"{EAVE_COLLECTOR_COOKIE_PREFIX}key": "value",
        }
        ctx.from_cookies(cookies)

        # non eave cookies should be skipped
        assert (
            ctx.to_json()
            == f'{{"{EAVE_COLLECTOR_COOKIE_PREFIX}session_id": "ses", "{EAVE_COLLECTOR_COOKIE_PREFIX}key": "value"}}'
        ), "Cookie conversion did not include only the expected cookies"

        # cookies should join join if existing ctx
        ctx.from_cookies(
            {f"{EAVE_COLLECTOR_COOKIE_PREFIX}visitor_id": "123", f"{EAVE_COLLECTOR_COOKIE_PREFIX}key": "new val"}
        )
        assert (
            ctx.to_json()
            == f'{{"{EAVE_COLLECTOR_COOKIE_PREFIX}session_id": "ses", "{EAVE_COLLECTOR_COOKIE_PREFIX}key": "new val", "{EAVE_COLLECTOR_COOKIE_PREFIX}visitor_id": "123"}}'
        ), "Context did not join as expected"

    async def test_convert_ctx_to_cookies_creates_valid_cookie(self) -> None:
        ctx = AsyncioCorrelationContext()
        ctx.set("session_id", "ses", encrypt=False)
        ctx.set("key", '"value"', encrypt=False)

        # expect URL encoded
        assert ctx.get_updated_values_cookies() == [
            f"{EAVE_COLLECTOR_COOKIE_PREFIX}session_id=ses",
            f"{EAVE_COLLECTOR_COOKIE_PREFIX}key=%22value%22",
        ], "Context cookie was converted incorrectly"
