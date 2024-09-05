from dataclasses import dataclass
import aiohttp
import uuid

from . import config


# NOTE: keep in sync w/ mirror definition eave-stdlib!
# (until pydantic dep is removed or we decide to have collectors depend on it too)
@dataclass(kw_only=True)
class DataCollectorConfig:
    id: uuid.UUID
    user_table_name_patterns: list[str]
    primary_key_patterns: list[str]
    foreign_key_patterns: list[str]


@dataclass(kw_only=True)
class DataCollectorConfigResponseBody:
    config: DataCollectorConfig


async def get_remote_config() -> DataCollectorConfig:
    if creds := config.EaveCredentials.from_env():
        headers = {**creds.to_headers}
    else:
        headers = None

    async with aiohttp.ClientSession() as session:
        resp = await session.request(
            method="POST",
            url=f"{config.eave_api_base_url()}/public/me/collector-configs/query",
            compress="gzip",
            headers=headers,
        )
        json_resp = await resp.json()
        remote_config = DataCollectorConfigResponseBody(**json_resp)
        return remote_config.config
