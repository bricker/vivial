import uuid
import redis.asyncio as redis
from redis.asyncio.retry import Retry
from redis.backoff import ConstantBackoff
from eave.core.config import CORE_API_APP_CONFIG
from eave.stdlib.logging import LOGGER

def _initialize_client() -> redis.Redis[bytes]:
    if redis_cfg := CORE_API_APP_CONFIG.redis_connection:
        klass = redis.Redis[bytes]
        host, port, db = redis_cfg
        auth_string = CORE_API_APP_CONFIG.redis_auth_string
        redis_tls_ca = CORE_API_APP_CONFIG.redis_tls_ca
    else:
        import fakeredis
        klass = fakeredis.aioredis.FakeRedis
        host = uuid.uuid4().hex # A stub host
        port = 6379
        db = "0"
        auth_string = None
        redis_tls_ca = None

    LOGGER.debug(f"Redis connection: klass={klass}, host={host}, port={port}, db={db}")

    return klass(
        client_name="core-api",
        host=host,
        port=port,
        db=db,
        password=auth_string,
        decode_responses=False,
        ssl=redis_tls_ca is not None,
        ssl_ca_data=redis_tls_ca,
        health_check_interval=60 * 5,
        socket_keepalive=True,
        retry=Retry(retries=2, backoff=ConstantBackoff(backoff=3)),
    )

CACHE = _initialize_client()
