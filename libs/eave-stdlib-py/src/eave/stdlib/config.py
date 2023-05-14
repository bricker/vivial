import enum
import logging
import os
import sys
from functools import cached_property

import google.cloud.secretmanager
import google.cloud.runtimeconfig

from . import checksum

# TODO: Use runtime-configs
# https://cloud.google.com/deployment-manager/runtime-configurator/create-and-delete-runtimeconfig-resources#gcloud
# config created called "shared-config"


class EaveEnvironment(enum.Enum):
    development = "development"
    production = "production"


class EaveConfig:
    @property
    def dev_mode(self) -> bool:
        return sys.flags.dev_mode

    @cached_property
    def log_level(self) -> int:
        mapping = logging.getLevelNamesMapping()
        if self.is_development:
            level = os.getenv("EAVE_LOG_LEVEL", "INFO")
        else:
            level = self.get_runtimeconfig("EAVE_LOG_LEVEL") or "INFO"
        return mapping.get(level, logging.INFO)

    @property
    def eave_env(self) -> EaveEnvironment:
        strenv = os.getenv("EAVE_ENV", "production")
        match strenv:
            case "development":
                return EaveEnvironment.development
            case "production":
                return EaveEnvironment.production
            case _:
                return EaveEnvironment.production

    @property
    def is_development(self) -> bool:
        return self.eave_env is EaveEnvironment.development

    @property
    def monitoring_enabled(self) -> bool:
        return os.getenv("EAVE_MONITORING_ENABLED") is not None

    @property
    def google_cloud_project(self) -> str:
        return self.get_required_env("GOOGLE_CLOUD_PROJECT")

    @property
    def app_service(self) -> str:
        return os.getenv("GAE_SERVICE", "unknown")

    @property
    def app_version(self) -> str:
        return os.getenv("GAE_VERSION", "unknown")

    @cached_property
    def eave_api_base(self) -> str:
        return self.get_runtimeconfig("EAVE_API_BASE") or "https://api.eave.fyi"

    @cached_property
    def eave_www_base(self) -> str:
        return self.get_runtimeconfig("EAVE_WWW_BASE") or "https://www.eave.fyi"

    @cached_property
    def eave_cookie_domain(self) -> str:
        return self.get_runtimeconfig("EAVE_COOKIE_DOMAIN") or ".eave.fyi"

    @cached_property
    def eave_openai_api_key(self) -> str:
        value = self.get_secret("OPENAI_API_KEY")
        return value

    @cached_property
    def eave_slack_system_bot_token(self) -> str:
        value = self.get_secret("SLACK_SYSTEM_BOT_TOKEN")
        return value

    @cached_property
    def eave_slack_app_id(self) -> str:
        value = self.get_runtimeconfig("EAVE_SLACK_APP_ID")
        assert value is not None
        return value

    @cached_property
    def eave_slack_client_id(self) -> str:
        return self.get_secret("EAVE_SLACK_APP_CLIENT_ID")

    @cached_property
    def eave_slack_client_secret(self) -> str:
        return self.get_secret("EAVE_SLACK_APP_CLIENT_SECRET")

    @cached_property
    def eave_atlassian_app_client_id(self) -> str:
        return self.get_secret("EAVE_ATLASSIAN_APP_CLIENT_ID")

    @cached_property
    def eave_atlassian_app_client_secret(self) -> str:
        return self.get_secret("EAVE_ATLASSIAN_APP_CLIENT_SECRET")

    def get_required_env(self, name: str) -> str:
        if name not in os.environ:
            raise KeyError(f"{name} is a required environment variable, but is not set.")

        return os.environ[name]

    def get_runtimeconfig(self, name: str) -> str | None:
        """
        https://cloud.google.com/python/docs/reference/runtimeconfig/latest
        https://github.com/googleapis/python-runtimeconfig
        """
        if self.is_development and name in os.environ:
            return os.environ[name]

        client = google.cloud.runtimeconfig.Client()
        config = client.config("eave-global-config")

        variable = config.get_variable(name)
        if variable is None:
            return None

        return variable.text

    def get_secret(self, name: str) -> str:
        if self.is_development and name in os.environ:
            return os.environ[name]

        secrets_client = google.cloud.secretmanager.SecretManagerServiceClient()

        fqname = f"projects/{self.google_cloud_project}/secrets/{name}/versions/latest"
        response = secrets_client.access_secret_version(request={"name": fqname})
        data = response.payload.data
        data_crc32c = response.payload.data_crc32c

        checksum.validate_checksum_or_exception(data=data, checksum=data_crc32c)
        return data.decode("UTF-8")


shared_config = EaveConfig()
