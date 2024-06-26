import asyncio
import os
import unittest

from eave.collectors.core.correlation_context import AsyncioCorrelationContext
from eave.collectors.core.correlation_context.base import EAVE_COLLECTOR_COOKIE_PREFIX


class AsyncioCorrelationContextTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        os.environ["EAVE_CREDENTIALS"] = "abc:123"
        await super().asyncSetUp()

    async def test_separate_async_task_ctx_cannot_access_each_others_data(self) -> None:
        async def _helper(keys) -> None:
            ctx = AsyncioCorrelationContext()
            for key in keys:
                ctx.set(key, "1")

            expected = "{" + ", ".join([f'"{k}": "1"' for k in keys]) + "}"
            assert ctx.to_json() == expected, "Context contained other than expected values"

        t1 = asyncio.create_task(_helper(["k1", "k2", "k3"]))
        t2 = asyncio.create_task(_helper(["k4", "k5", "k6"]))
        await asyncio.gather(t1, t2)

    async def test_child_tasks_inherit_parent_ctx_values(self) -> None:
        ctx = AsyncioCorrelationContext()
        # given values exist in parent context
        ctx.set("parent", "0")

        async def task1() -> None:
            assert ctx.get("parent") == "0", "Parent value not present in child task t1"
            ctx.set("t1", "1")

        async def task2() -> None:
            assert ctx.get("parent") == "0", "Parent value not present in child task t2"
            ctx.set("t2", "2")

        t1 = asyncio.create_task(task1())
        t2 = asyncio.create_task(task2())
        await asyncio.gather(t1, t2)

        assert ctx.to_json() == '{"parent": "0", "t1": "1", "t2": "2"}', "Values set by child tasks not found"
