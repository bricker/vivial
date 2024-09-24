import aiohttp

from eave.collectors.core.logging import EAVE_CORE_LOGGER

from . import config


async def init_remote_config() -> None:
    remote_flag = "remote_source"
    if getattr(config.remote_config, remote_flag, False):
        return
    try:
        if creds := config.EaveCredentials.from_env():
            headers = {**creds.to_headers}
        else:
            headers = None

        async with aiohttp.ClientSession() as session:
            resp = await session.request(
                method="POST",
                url=f"{config.eave_api_base_url()}/public/collector-configs/query",
                compress="gzip",
                headers=headers,
            )
            json_resp = await resp.json()
            config.remote_config = config.DataCollectorConfig(**json_resp["config"])
            setattr(config.remote_config, remote_flag, True)
    except Exception as e:
        EAVE_CORE_LOGGER.error("Failed to fetch Eave remote config; using fallback config", extra={"error": e})
