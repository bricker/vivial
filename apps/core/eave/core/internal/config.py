import json
import os
from functools import cached_property
from typing import Any

from eave.stdlib.config import SHARED_CONFIG, ConfigBase, get_required_env, get_secret
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

    @cached_property
    def eave_google_oauth_client_credentials(self) -> dict[str, Any]:
        b64encoded = get_secret("EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_JSON_B64")
        json_encoded = b64decode(b64encoded)
        credentials: dict[str, Any] = json.loads(json_encoded)
        return credentials

    @property
    def eave_google_oauth_client_id(self) -> str:
        credentials = self.eave_google_oauth_client_credentials
        client_id: str = credentials["web"]["client_id"]
        return client_id


CORE_API_APP_CONFIG = _AppConfig()
