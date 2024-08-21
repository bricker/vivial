from typing import Any

import aiohttp

from eave.collectors.core.datastructures import Batchable, DataIngestRequestBody, LogPayload

from ... import config
from . import DataHandler


class LogsHandler(DataHandler):
    def validate_data_type(self, payload: Any) -> bool:
        return isinstance(payload, LogPayload)

    async def send_buffer(self, buffer: list[Batchable]) -> None:
        if len(buffer) == 0:
            return

        # TODO: convert to send log events
        body = DataIngestRequestBody(events=events)

        if creds := config.EaveCredentials.from_env():
            headers = {**creds.to_headers}
        else:
            headers = None

        # TODO: send to proper endpoidn
        async with aiohttp.ClientSession() as session:
            await session.request(
                method="POST",
                url=f"{config.eave_api_base_url()}/public/ingest/server",
                data=body.to_json(),
                compress="gzip",
                headers=headers,
            )
