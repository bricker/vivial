import json
import os
from functools import cached_property
from typing import Any

from eave.stdlib.config import ConfigBase, get_secret
from eave.stdlib.eave_origins import EaveApp
from eave.stdlib.util import b64decode


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


CORE_API_APP_CONFIG = _AppConfig()
