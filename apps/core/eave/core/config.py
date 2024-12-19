import os
from functools import cached_property

from eave.stdlib.config import SHARED_CONFIG, ConfigBase, EaveEnvironment, get_secret

JWT_ISSUER = "core-api"
JWT_AUDIENCE = "core-api"


class _AppConfig(ConfigBase):
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
        return get_secret("EVENTBRITE_API_KEY")

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


CORE_API_APP_CONFIG = _AppConfig()
