import logging
import os
from functools import cached_property
from typing import Optional

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
    def db_host(self) -> Optional[str]:
        return os.getenv("EAVE_DB_HOST")

    @property
    def db_port(self) -> Optional[int]:
        port = os.getenv("EAVE_DB_PORT")
        if port is None:
            return None
        return int(port)

    @property
    def google_cloud_project(self) -> Optional[str]:
        return os.getenv("GOOGLE_CLOUD_PROJECT")

    @property
    def monitoring_enabled(self) -> bool:
        return os.getenv("EAVE_MONITORING_ENABLED") is not None

    @property
    def db_user(self) -> Optional[str]:
        return self.get_secret("DB_USER")

    @cached_property
    def db_pass(self) -> Optional[str]:
        return self.get_secret("DB_PASS")

    @cached_property
    def eave_openapi_key(self) -> Optional[str]:
        return self.get_secret("OPENAI_API_KEY")

    @cached_property
    def eave_slack_system_bot_token(self) -> Optional[str]:
        return self.get_secret("SLACK_SYSTEM_BOT_TOKEN")

    def get_secret(self, name: str) -> Optional[str]:
        env_value = os.getenv(name)
        if env_value is not None:
            return env_value

        if self.google_cloud_project is None:
            logging.warn("GOOGLE_CLOUD_PROJECT not specified; can't connect to GCP.")
            return None

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
