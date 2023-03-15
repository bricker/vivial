import logging
import os
import sys
from functools import cache, cached_property
from typing import Optional

import google_crc32c
from google.cloud import secretmanager


class Settings:
    @property
    def dev_mode(self) -> bool:
        return sys.flags.dev_mode

    @property
    def eave_core_api_url(self) -> str:
        return os.environ["EAVE_CORE_API_URL"]

    @property
    def eave_slack_app_id(self) -> str:
        return os.environ["EAVE_SLACK_APP_ID"]

    @property
    def eave_team_id(self) -> str:
        # TODO: This needs to come from a mapping of Slack Installation ID -> Team
        return os.environ["EAVE_TEAM_ID"]

    @property
    def monitoring_enabled(self) -> bool:
        return os.getenv("EAVE_MONITORING_ENABLED") is not None

    @property
    def google_cloud_project(self) -> Optional[str]:
        return os.getenv("GOOGLE_CLOUD_PROJECT")

    @cached_property
    def eave_signing_secret(self) -> str:
        value = self.get_secret("EAVE_SIGNING_SECRET")
        assert value is not None
        return value

    @cached_property
    def eave_openai_api_key(self) -> Optional[str]:
        return self.get_secret("OPENAI_API_KEY")

    @cached_property
    def eave_slack_app_token(self) -> Optional[str]:
        return self.get_secret("SLACK_APP_TOKEN")

    @cached_property
    def eave_slack_bot_token(self) -> Optional[str]:
        return self.get_secret("SLACK_BOT_TOKEN")

    @cached_property
    def eave_slack_bot_signing_secret(self) -> Optional[str]:
        return self.get_secret("SLACK_SIGNING_SECRET")

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
