import aiohttp

from . import config
from .datastructures import DataIngestRequestBody, EventType


async def send_batch(event_type: EventType, events: list[str]) -> None:
    async with aiohttp.ClientSession() as session:
        body = DataIngestRequestBody(event_type=event_type, events=events)
        await session.request(
            method="POST",
            url=f"{config.eave_api_base_url()}/v1/ingest",
            data=body.to_json(),
            compress="gzip",
            headers={
                **config.eave_credentials_headers(),
            },
        )
