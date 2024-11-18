import os
from functools import cached_property

from eave.stdlib.config import ConfigBase, get_required_env

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
        return get_required_env("EVENTBRITE_API_KEY")

    @cached_property
    def segment_write_key(self) -> str:
        return get_required_env("SEGMENT_CORE_API_WRITE_KEY")


CORE_API_APP_CONFIG = _AppConfig()
