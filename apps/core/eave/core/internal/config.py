import json
import os
from collections.abc import Mapping
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
    def db_host(self) -> str:
        key = "EAVE_DB_HOST"
        if SHARED_CONFIG.is_development:
            return get_required_env(key)
        else:
            return get_secret(key)

    @cached_property
    def db_port(self) -> int | None:
        key = "EAVE_DB_PORT"
        if SHARED_CONFIG.is_development:
            strv = os.getenv(key)
            if strv is None:
                return None
            else:
                return int(strv)
        else:
            try:
                strv = get_secret(key)
                return int(strv)
            except Exception:
                return None

    @cached_property
    def db_user(self) -> str:
        key = "EAVE_DB_USER"
        if SHARED_CONFIG.is_development:
            return get_required_env(key)
        else:
            return get_secret(key)

    @cached_property
    def db_pass(self) -> str | None:
        key = "EAVE_DB_PASS"
        if SHARED_CONFIG.is_development:
            value = os.getenv(key)
            # Treat empty strings as None
            return None if not value else value
        else:
            try:
                return get_secret(key)
            except Exception:
                return None

    @cached_property
    def db_name(self) -> str:
        key = "EAVE_DB_NAME"
        if SHARED_CONFIG.is_development:
            return get_required_env(key)
        else:
            return get_secret(key)

    @cached_property
    def eave_google_oauth_client_credentials(self) -> Mapping[str, Any]:
        b64encoded = get_secret("EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_JSON_B64")
        json_encoded = b64decode(b64encoded)
        credentials: dict[str, Any] = json.loads(json_encoded)
        return credentials

    @cached_property
    def eave_google_oauth_client_id(self) -> str:
        credentials = self.eave_google_oauth_client_credentials
        client_id: str = credentials["web"]["client_id"]
        return client_id

    @property
    def metabase_jwt_key(self) -> str:
        # This comes from the environment because it's defined as a Kubernetes secret for consumption by the Metabase app.
        # The alternative is to set the JWT key in both the environment (for Metabase) and Secret Manager (for core API),
        # and keep them in sync, but it's easier to use a single source.
        key = "MB_JWT_SHARED_SECRET"
        return get_required_env(key)


CORE_API_APP_CONFIG = _AppConfig()
