from functools import cache
import aiohttp
from eave.stdlib.config import ConfigBase, get_required_env


class _AppConfig(ConfigBase):
    @property
    def iap_jwt_aud(self) -> str:
        return get_required_env("EAVE_ADMIN_IAP_JWT_AUD")

ADMIN_APP_CONFIG = _AppConfig()
