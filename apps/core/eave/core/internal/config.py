import os
from functools import cached_property

from eave.stdlib.config import ConfigBase
from eave.stdlib.eave_origins import EaveApp


class _AppConfig(ConfigBase):
    @property
    def eave_origin(self) -> EaveApp:
        return EaveApp.eave_api

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
    def google_places_api_key(self) -> str:
        value = os.getenv("GOOGLE_PLACES_API_KEY")
        assert value is not None, "Google Places API key not set"
        return value

    @cached_property
    def eventbrite_api_key(self) -> str:
        value = os.getenv("EVENTBRITE_API_KEY")
        assert value is not None, "Eventbrite API key not set"
        return value


CORE_API_APP_CONFIG = _AppConfig()
