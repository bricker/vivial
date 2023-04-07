import os
import sys
from functools import cached_property

import google_crc32c
from google.cloud import secretmanager


class EaveConfig:
    @property
    def dev_mode(self) -> bool:
        return sys.flags.dev_mode

    @property
    def monitoring_enabled(self) -> bool:
        return os.getenv("EAVE_MONITORING_ENABLED") is not None

    @property
    def eave_api_base(self) -> str:
        return os.getenv("EAVE_API_BASE", "https://api.eave.fyi")

    @property
    def eave_www_base(self) -> str:
        return os.getenv("EAVE_WWW_BASE", "https://www.eave.fyi")

    @property
    def eave_cookie_domain(self) -> str:
        return os.getenv("EAVE_COOKIE_DOMAIN", ".eave.fyi")

    @property
    def google_cloud_project(self) -> str:
        value = os.getenv("GOOGLE_CLOUD_PROJECT")
        assert value is not None
        return value

    @property
    def app_service(self) -> str:
        return os.getenv("GAE_SERVICE", "unknown")

    @property
    def app_version(self) -> str:
        return os.getenv("GAE_VERSION", "unknown")

    @cached_property
    def eave_signing_secret(self) -> str:
        value = self.get_secret("EAVE_SIGNING_SECRET")
        return value

    @cached_property
    def eave_openai_api_key(self) -> str:
        value = self.get_secret("OPENAI_API_KEY")
        return value

    @cached_property
    def eave_slack_system_bot_token(self) -> str:
        value = self.get_secret("SLACK_SYSTEM_BOT_TOKEN")
        return value

    @cached_property
    def eave_slack_client_id(self) -> str:
        value: str = self.get_secret("EAVE_SLACK_APP_CLIENT_ID")
        return value

    @cached_property
    def eave_slack_client_secret(self) -> str:
        value: str = self.get_secret("EAVE_SLACK_APP_CLIENT_SECRET")
        return value

    def get_secret(self, name: str) -> str:
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


shared_config = EaveConfig()
