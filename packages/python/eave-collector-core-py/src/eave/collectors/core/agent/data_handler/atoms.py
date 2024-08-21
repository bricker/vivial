from typing import Any

import aiohttp

from eave.collectors.core import config
from eave.collectors.core.datastructures import Batchable, DataIngestRequestBody, EventPayload
from eave.collectors.core.json import JsonObject

from . import DataHandler


class AtomHandler(DataHandler):
    def validate_data_type(self, payload: Any) -> bool:
        return isinstance(payload, EventPayload)

    async def send_buffer(self, buffer: list[Batchable]) -> None:
        if len(buffer) == 0:
            return

        grouped_events: dict[str, list[JsonObject]] = {}
        for payload in buffer:
            if not isinstance(payload, EventPayload):
                continue

            key = str(payload.event_type)
            val = payload.to_dict()
            if key in grouped_events:
                grouped_events[key].append(val)
            else:
                grouped_events[key] = [val]

        body = DataIngestRequestBody(events=grouped_events)

        if creds := config.EaveCredentials.from_env():
            headers = {**creds.to_headers}
        else:
            headers = None

        async with aiohttp.ClientSession() as session:
            await session.request(
                method="POST",
                url=f"{config.eave_api_base_url()}/public/ingest/server",
                data=body.to_json(),
                compress="gzip",
                headers=headers,
            )
