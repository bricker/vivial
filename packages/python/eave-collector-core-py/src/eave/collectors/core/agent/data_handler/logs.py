import aiohttp

from eave.collectors.core.datastructures import LogIngestRequestBody, LogPayload

from ... import config
from . import DataHandler


class LogsHandler(DataHandler[LogPayload]):
    async def send_buffer(self, buffer: list[LogPayload]) -> None:
        if len(buffer) == 0:
            return

        logs = []
        for log in buffer:
            if not isinstance(log, LogPayload):
                continue
            logs.append(log.to_dict())

        body = LogIngestRequestBody(logs=logs)

        if creds := config.EaveCredentials.from_env():
            headers = {**creds.to_headers}
        else:
            headers = None

        async with aiohttp.ClientSession() as session:
            await session.request(
                method="POST",
                url=f"{config.eave_api_base_url()}/public/ingest/log",
                data=body.to_json(),
                compress="gzip",
                headers=headers,
            )
