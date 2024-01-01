import asyncio
import aiohttp

from eave.stdlib.nettracing.py_agent import trace_network

async def test_request() -> None:
    async with aiohttp.ClientSession() as sess:
        async with sess.get("https://www.google.com") as resp:
            body = await resp.text()
            print(f"test got {body}")

trace_network()
asyncio.run(test_request())