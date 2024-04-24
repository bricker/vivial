import aiohttp

from .config import EAVE_API_BASE_URL
from .datastructures import DataIngestRequestBody, EventType


async def send_batch(event_type: EventType, events: list[str]) -> None:
    async with aiohttp.ClientSession() as session:
        body = DataIngestRequestBody(event_type=event_type, events=events)
        await session.request(
            method="POST",
            url=f"{EAVE_API_BASE_URL}/v1/ingest",
            data=body.to_json(),
            compress="gzip",
            headers={
                "eave-client-id": "TKTKTK",
                "eave-client-secret": "TKTKTK",
            },
        )
