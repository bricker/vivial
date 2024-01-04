import dataclasses
import json
from typing import Any
import aiohttp

from eave.monitoring.config import EAVE_API_BASE_URL
from eave.monitoring.datastructures import DataIngestRequestBody, EventType, RawEvent

async def send_data(event_type: EventType, events: list[str]) -> None:
    async with aiohttp.ClientSession() as session:
        body = DataIngestRequestBody(event_type=event_type, events=events)

        await session.request(
            method="POST",
            url=f"{EAVE_API_BASE_URL}/ingest",
            compress="gzip",
            data=body.to_json()
        )
