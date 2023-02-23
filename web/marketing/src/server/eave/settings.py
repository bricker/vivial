import base64
import json
import os
from functools import cached_property
from typing import Any, Mapping, Optional

import eave.util
from google.cloud import secretmanager


class Settings:
    @property
    def google_cloud_project(self) -> str:
        value = os.getenv("GOOGLE_CLOUD_PROJECT")
        assert value is not None
        return value

    @property
    def app_env(self) -> str:
        if os.getenv("FLASK_DEBUG") is not None:
            return "development"
        else:
            return "production"

    @property
    def analytics_enabled(self) -> bool:
        return os.getenv("EAVE_ANALYTICS_ENABLED") is not None

    @property
    def monitoring_enabled(self) -> bool:
        return os.getenv("EAVE_MONIORING_ENABLED") is not None

    @property
    def app_version(self) -> str:
        return os.getenv("GAE_VERSION", "development")

    @property
    def eave_cookie_domain(self) -> str:
        return os.getenv("EAVE_COOKIE_DOMAIN", ".eave.fyi")

    @property
    def eave_api_base(self) -> str:
        return os.getenv("EAVE_API_BASE", "https://api.eave.fyi")

    @property
    def asset_base(self) -> str:
        return os.getenv("EAVE_ASSET_BASE", "/static")

    @cached_property
    def eave_web_session_encryption_key(self) -> str:
        key = self.get_secret("EAVE_WEB_SESSION_ENCRYPTION_KEY")
        assert key is not None
        return key

    def get_secret(self, name: str) -> Optional[str]:
        env_value = os.getenv(name)
        if env_value is not None:
            return env_value

        secrets_client = secretmanager.SecretManagerServiceClient()

        fqname = f"projects/{self.google_cloud_project}/secrets/{name}/versions/latest"
        response = secrets_client.access_secret_version(request={"name": fqname})
        data = response.payload.data

        crc32c = eave.util.crc32c(data)
        if response.payload.data_crc32c != crc32c:
            raise Exception("Data corruption detected.")

        return data.decode("UTF-8")


APP_SETTINGS = Settings()
