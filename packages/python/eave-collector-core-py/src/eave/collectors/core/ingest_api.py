import aiohttp

from . import config
from .datastructures import DataIngestRequestBody
from .json import JsonObject


async def send_batch(events: dict[str, list[JsonObject]]) -> None:
    body = DataIngestRequestBody(events=events)

    async with aiohttp.ClientSession() as session:
        await session.request(
            method="POST",
            url=f"{config.eave_api_base_url()}/public/ingest/server",
            data=body.to_json(),
            compress="gzip",
            headers={
                **config.eave_credentials_headers(),
            },
        )
