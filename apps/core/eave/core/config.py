import json
import os
from functools import cached_property

from eave.stdlib.config import SHARED_CONFIG, ConfigBase, EaveEnvironment, get_required_env, get_secret

JWT_ISSUER = "core-api"
JWT_AUDIENCE = "core-api"


class _AppConfig(ConfigBase):
    @property
    def internal_iap_enabled(self) -> bool:
        # IAP at /iap is always enabled in non-local environments
        return not SHARED_CONFIG.is_local

    @property
    def internal_iap_jwt_aud(self) -> str | None:
        if self.internal_iap_enabled:
            return get_required_env("EAVE_API_INTERNAL_IAP_JWT_AUD")
        else:
            return None

    @property
    def root_iap_enabled(self) -> bool:
        return os.getenv("EAVE_API_ROOT_IAP_ENABLED") == "1"

    @property
    def root_iap_jwt_aud(self) -> str | None:
        if self.root_iap_enabled:
            return get_required_env("EAVE_API_ROOT_IAP_JWT_AUD")
        else:
            return None

    @cached_property
    def db_host(self) -> str | None:
        key = "EAVE_DB_HOST"
        return os.getenv(key)

    @cached_property
    def db_port(self) -> int | None:
        key = "EAVE_DB_PORT"
        strv = os.getenv(key)
        if strv is None:
            return None
        else:
            return int(strv)

    @cached_property
    def db_user(self) -> str | None:
        key = "EAVE_DB_USER"
        return os.getenv(key)

    @cached_property
    def db_pass(self) -> str | None:
        key = "EAVE_DB_PASS"
        value = os.getenv(key)
        # Treat empty strings as None
        return None if not value else value

    @cached_property
    def db_name(self) -> str:
        key = "EAVE_DB_NAME"
        return os.getenv(key, "eave")

    @cached_property
    def eventbrite_api_key(self) -> str:
        api_keys = self.eventbrite_api_keys
        return api_keys[0]

    @cached_property
    def eventbrite_api_keys(self) -> list[str]:
        val = get_secret("EVENTBRITE_API_KEYS")
        return json.loads(val)

    @property
    def segment_write_key(self) -> str:
        match SHARED_CONFIG.eave_env:
            case EaveEnvironment.test | EaveEnvironment.development:
                return "ZzSxy8sDYNbSHeIaKKTL4ESAupEX6ufV"  # Not Sensitive
            case EaveEnvironment.staging:
                return "uUjBMbm9CcTL9XV1Rf6S9xGpLnvtCObZ"  # Not Sensitive
            case EaveEnvironment.production:
                return "cVBM36ZvqJV2gagtnOT60fTNn1Q5P5na"  # Not Sensitive

    @cached_property
    def stripe_secret_key(self) -> str:
        return get_secret("STRIPE_SECRET_KEY")

    @cached_property
    def google_maps_api_key(self) -> str:
        return get_secret("GOOGLE_MAPS_API_KEY")


CORE_API_APP_CONFIG = _AppConfig()
