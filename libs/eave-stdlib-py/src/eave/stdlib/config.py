import os
import sys
from functools import cached_property

from google.cloud import secretmanager, runtimeconfig
from . import checksum


# TODO: Use runtime-configs
# https://cloud.google.com/deployment-manager/runtime-configurator/create-and-delete-runtimeconfig-resources#gcloud
# config created called "shared-config"

class EaveConfig:
    @property
    def dev_mode(self) -> bool:
        return sys.flags.dev_mode

    @property
    def monitoring_enabled(self) -> bool:
        return os.getenv("EAVE_MONITORING_ENABLED") is not None

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
    def eave_api_base(self) -> str:
        value = self.get_runtimeconfig("EAVE_API_BASE") or "https://api.eave.fyi"
        return value

    @cached_property
    def eave_www_base(self) -> str:
        value = self.get_runtimeconfig("EAVE_WWW_BASE") or "https://www.eave.fyi"
        return value

    @cached_property
    def eave_cookie_domain(self) -> str:
        value = self.get_runtimeconfig("EAVE_COOKIE_DOMAIN") or ".eave.fyi"
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
    def eave_slack_app_id(self) -> str:
        value = self.get_runtimeconfig("EAVE_SLACK_APP_ID")
        assert value is not None
        return value

    @cached_property
    def eave_slack_client_id(self) -> str:
        value: str = self.get_secret("EAVE_SLACK_APP_CLIENT_ID")
        return value

    @cached_property
    def eave_slack_client_secret(self) -> str:
        value: str = self.get_secret("EAVE_SLACK_APP_CLIENT_SECRET")
        return value

    @cached_property
    def eave_atlassian_app_client_id(self) -> str:
        value: str = self.get_secret("EAVE_ATLASSIAN_APP_CLIENT_ID")
        return value

    @cached_property
    def eave_atlassian_app_client_secret(self) -> str:
        value: str = self.get_secret("EAVE_ATLASSIAN_APP_CLIENT_SECRET")
        return value

    def get_runtimeconfig(self, name: str) -> str | None:
        """
        https://cloud.google.com/python/docs/reference/runtimeconfig/latest
        https://github.com/googleapis/python-runtimeconfig
        """
        env_value = os.getenv(name)
        if env_value is not None:
            return env_value

        client = runtimeconfig.Client()
        config = client.config("eave-global-config")

        variable = config.get_variable(name)
        if not variable:
            return None

        value: str | None = variable.text
        return value

    def get_secret(self, name: str) -> str:
        env_value = os.getenv(name)
        if env_value is not None:
            return env_value

        secrets_client = secretmanager.SecretManagerServiceClient()

        fqname = f"projects/{self.google_cloud_project}/secrets/{name}/versions/latest"
        response = secrets_client.access_secret_version(request={"name": fqname})
        data = response.payload.data
        data_crc32c = response.payload.data_crc32c

        checksum.validate_checksum_or_exception(data=data, checksum=data_crc32c)
        return data.decode("UTF-8")


shared_config = EaveConfig()
