import base64
import json
import os
from functools import cached_property
from typing import Any, Mapping, Optional

import google_crc32c
from google.cloud import secretmanager


class Settings:
    @property
    def db_connection_string(self) -> Optional[str]:
        return os.getenv("EAVE_DB_CONNECTION_STRING")

    @property
    def db_driver(self) -> str:
        return os.getenv("EAVE_DB_DRIVER", "postgresql+asyncpg")

    @property
    def db_name(self) -> str:
        return os.getenv("EAVE_DB_NAME", "eave")

    @property
    def db_host(self) -> str:
        value = os.getenv("EAVE_DB_HOST")
        assert value is not None
        return value

    @property
    def db_port(self) -> Optional[int]:
        port = os.getenv("EAVE_DB_PORT")
        if port is None:
            return None
        return int(port)

    @property
    def google_cloud_project(self) -> str:
        value = os.getenv("GOOGLE_CLOUD_PROJECT")
        assert value is not None
        return value

    @property
    def monitoring_enabled(self) -> bool:
        return os.getenv("EAVE_MONITORING_ENABLED") is not None

    @property
    def db_user(self) -> str:
        value = self.get_secret("DB_USER")
        assert value is not None
        return value

    @cached_property
    def db_pass(self) -> str:
        value = self.get_secret("DB_PASS")
        assert value is not None
        return value

    @property
    def eave_demo_mode(self) -> bool:
        return os.getenv("EAVE_DEMO_MODE") is not None

    @property
    def eave_cookie_domain(self) -> str:
        return os.getenv("EAVE_COOKIE_DOMAIN", ".eave.fyi")

    @property
    def eave_api_base(self) -> str:
        return os.getenv("EAVE_API_BASE", "https://api.eave.fyi")

    @property
    def eave_www_base(self) -> str:
        return os.getenv("EAVE_WWW_BASE", "https://www.eave.fyi")

    @cached_property
    def eave_openapi_key(self) -> str:
        value = self.get_secret("OPENAI_API_KEY")
        assert value is not None
        return value

    @cached_property
    def eave_slack_system_bot_token(self) -> str:
        value = self.get_secret("SLACK_SYSTEM_BOT_TOKEN")
        assert value is not None
        return value

    @cached_property
    def eave_google_oauth_client_credentials(self) -> Mapping[str, Any]:
        encoded = self.get_secret("EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_B64")
        assert encoded is not None
        bytes = base64.b64decode(encoded)
        credentials: dict[str, Any] = json.loads(bytes)
        return credentials

    @cached_property
    def eave_google_oauth_client_id(self) -> str:
        client_id: str = self.eave_google_oauth_client_credentials["web"]["client_id"]
        return client_id

    def get_secret(self, name: str) -> Optional[str]:
        env_value = os.getenv(name)
        if env_value is not None:
            return env_value

        secrets_client = secretmanager.SecretManagerServiceClient()

        fqname = f"projects/{self.google_cloud_project}/secrets/{name}/versions/latest"
        response = secrets_client.access_secret_version(request={"name": fqname})
        data = response.payload.data

        crc32c = google_crc32c.Checksum()
        crc32c.update(data)
        if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
            raise Exception("Data corruption detected.")

        return data.decode("UTF-8")


APP_SETTINGS = Settings()
