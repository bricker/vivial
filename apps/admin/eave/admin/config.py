from eave.stdlib.config import SHARED_CONFIG, ConfigBase, get_required_env


class _AppConfig(ConfigBase):
    @property
    def iap_enabled(self) -> bool:
        return not SHARED_CONFIG.is_local

    @property
    def iap_jwt_aud(self) -> str | None:
        if self.iap_enabled:
            return get_required_env("EAVE_ADMIN_IAP_JWT_AUD")
        else:
            return None


ADMIN_APP_CONFIG = _AppConfig()
