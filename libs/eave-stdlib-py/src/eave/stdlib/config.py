import enum
import logging
import os
import sys
from functools import cached_property
from typing import Optional, Self

import google.cloud.secretmanager
import google.cloud.runtimeconfig
import google.cloud.client


from . import checksum


class EaveEnvironment(enum.StrEnum):
    development = "development"
    production = "production"


class EaveConfig:
    def preload(self) -> Self:
        """
        This is meant to be used in a GAE warmup request to preload all of the remote configs.
        """
        for attrname, attrfunc in self.__class__.__dict__.items():
            if type(attrfunc) == cached_property:
                getattr(self, attrname)

        return self

    @property
    def dev_mode(self) -> bool:
        return sys.flags.dev_mode

    @property
    def log_level(self) -> int:
        level = os.getenv("LOG_LEVEL", "INFO")
        mapping = logging.getLevelNamesMapping()
        return mapping.get(level.upper(), logging.INFO)

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
    def raise_app_exceptions(self) -> bool:
        """
        This is intended for using during development.
        When set to True, unhandled exceptions raised during the request won't be handled.
        In production (i.e. when this flag is False), unhandled exceptions are caught, logged, and return a 500.
        """
        return self.is_development

    @property
    def monitoring_enabled(self) -> bool:
        return os.getenv("EAVE_MONITORING_ENABLED") is not None

    @property
    def analytics_enabled(self) -> bool:
        return os.getenv("EAVE_ANALYTICS_ENABLED") is not None

    @property
    def google_cloud_project(self) -> str:
        return self.get_required_env("GOOGLE_CLOUD_PROJECT")

    @property
    def app_service(self) -> str:
        return os.getenv("GAE_SERVICE", "unknown")

    @property
    def app_version(self) -> str:
        return os.getenv("GAE_VERSION", "unknown")

    @property
    def app_location(self) -> str:
        return os.getenv("GAE_LOCATION") or "us-central1"

    @property
    def eave_apps_base(self) -> str:
        return os.getenv("EAVE_APPS_BASE") or "https://apps.eave.fyi"

    @property
    def eave_api_base(self) -> str:
        return os.getenv("EAVE_API_BASE") or "https://api.eave.fyi"

    @property
    def eave_www_base(self) -> str:
        return os.getenv("EAVE_WWW_BASE") or "https://www.eave.fyi"

    @property
    def eave_cookie_domain(self) -> str:
        return os.getenv("EAVE_COOKIE_DOMAIN") or ".eave.fyi"

    @property
    def redis_connection(self) -> Optional[tuple[str, int, str]]:
        connection = os.getenv("REDIS_CONNECTION")

        if not connection:
            return None

        parts = connection.split(":")
        if len(parts) == 3:
            host, port_, db = parts
            port = int(port_)
        elif len(parts) == 2:
            host, port_ = parts
            port = int(port_)
            db = "0"
        else:
            host = parts[0]
            port = 6379
            db = "0"

        return (host, port, db)

    @cached_property
    def redis_auth(self) -> Optional[str]:
        key = "REDIS_AUTH"
        if self.is_development:
            value = os.getenv(key)
            return value
        else:
            try:
                value = self.get_secret(key)
                return value
            except Exception:
                return None

    @property
    def redis_tls_ca(self) -> Optional[str]:
        return os.getenv("REDIS_TLS_CA")

    @property
    def eave_beta_whitelist_disabled(self) -> bool:
        try:
            value = self.get_secret("EAVE_BETA_WHITELIST_DISABLED")
            return value == "1"
        except Exception:
            # Beta whitelist secret doesn't exist
            return False

    @cached_property
    def eave_openai_api_key(self) -> str:
        value = self.get_secret("OPENAI_API_KEY")
        return value

    @cached_property
    def eave_slack_system_bot_token(self) -> str:
        value = self.get_secret("SLACK_SYSTEM_BOT_TOKEN")
        return value

    @property
    def eave_slack_app_id(self) -> str:
        # TODO: Change this secret or metadata
        return os.getenv("EAVE_SLACK_APP_ID", "A04HD948UHE")  # This is the production ID, and won't change.

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

    @cached_property
    def eave_github_app_public_url(self) -> str:
        return self.get_secret("EAVE_GITHUB_APP_PUBLIC_URL")

    def get_required_env(self, name: str) -> str:
        if name not in os.environ:
            raise KeyError(f"{name} is a required environment variable, but is not set.")

        return os.environ[name]

    # TODO: Can/should we use Runtime Config? It's nifty but adds extra network requests.
    # def get_runtimeconfig(self, name: str) -> str | None:
    #     """
    #     https://cloud.google.com/python/docs/reference/runtimeconfig/latest
    #     https://github.com/googleapis/python-runtimeconfig
    #     """
    #     # Allow overrides
    #     if name in os.environ:
    #         return os.environ[name]

    #     client = google.cloud.runtimeconfig.Client()
    #     config = client.config("eave-global-config")

    #     variable = config.get_variable(name)
    #     if variable is None:
    #         return None

    #     return variable.text

    def get_secret(self, name: str) -> str:
        # Allow overrides
        if name in os.environ:
            return os.environ[name]

        secrets_client = google.cloud.secretmanager.SecretManagerServiceClient()
        fqname = secrets_client.secret_version_path(
            project=self.google_cloud_project,
            secret=name,
            secret_version="latest",
        )
        response = secrets_client.access_secret_version(request={"name": fqname})
        data = response.payload.data
        data_crc32c = response.payload.data_crc32c

        checksum.validate_checksum_or_exception(data=data, checksum=data_crc32c)
        return data.decode("UTF-8")


shared_config = EaveConfig()
