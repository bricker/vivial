import enum
import logging
import os
import re
import sys
from functools import cached_property
from typing import Self
from urllib.parse import urlparse

import google.cloud.secretmanager
import google.cloud.runtimeconfig
import google.cloud.client
import google.cloud.redis as _gredis
import google.cloud.compute as _gcompute

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
        k = "EAVE_APPS_BASE"
        if v := os.getenv(k):
            return v
        else:
            return self.gcp_metadata.get(k, "https://apps.eave.fyi")

    @property
    def eave_api_base(self) -> str:
        k = "EAVE_API_BASE"
        if v := os.getenv(k):
            return v
        else:
            return self.gcp_metadata.get(k, "https://api.eave.fyi")

    @property
    def eave_www_base(self) -> str:
        k = "EAVE_WWW_BASE"
        if v := os.getenv(k):
            return v
        else:
            return self.gcp_metadata.get(k, "https://www.eave.fyi")

    @property
    def eave_apex_domain(self) -> str:
        parsed = urlparse(self.eave_www_base)
        host = parsed.hostname or "www.eave.fyi"
        return re.sub("^www.", "", host)

    @property
    def eave_cookie_domain(self) -> str:
        return f".{self.eave_apex_domain}"

    @cached_property
    def redis_instance(self) -> _gredis.Instance | None:
        """
        To use redis in local development, set REDIS_HOST in your environment, and optionally REDIS_PORT.
        """
        if self.is_development:
            if host := os.getenv("REDIS_HOST"):
                return _gredis.Instance(
                    name="development",
                    host=host,
                    port=int(os.getenv("REDIS_PORT", "6378")),
                    transit_encryption_mode=_gredis.Instance.TransitEncryptionMode.TRANSIT_ENCRYPTION_MODE_UNSPECIFIED,
                    server_ca_certs=[],
                )
            else:
                return None
        else:
            client = _gredis.CloudRedisClient()
            return client.get_instance(
                name=client.instance_path(
                    project=self.google_cloud_project,
                    location="us-central1",
                    instance=self.gcp_metadata.get("REDIS_INSTANCE_ID", "redis-core"),
                )
            )

    @cached_property
    def redis_auth(self) -> str | None:
        if self.is_development:
            return os.getenv("REDIS_AUTH")

        elif instance := self.redis_instance:
            client = _gredis.CloudRedisClient()
            auth = client.get_instance_auth_string(
                name=instance.name,
            )
            return auth.auth_string

        else:
            return None

    @property
    def redis_cache_db(self) -> str:
        k = "REDIS_CACHE_DB"
        if v := os.getenv(k):
            return v
        else:
            return self.gcp_metadata.get(k, "0")

    @property
    def eave_beta_whitelist_disabled(self) -> bool:
        k = "EAVE_BETA_WHITELIST_DISABLED"
        if v := os.getenv(k):
            return v == "1"
        else:
            return self.gcp_metadata.get(k) == "1"

    @cached_property
    def eave_openai_api_key(self) -> str:
        value = self.get_secret("OPENAI_API_KEY")
        return value

    @cached_property
    def eave_openai_api_org(self) -> str:
        value = self.get_secret("OPENAI_API_ORG")
        return value

    @cached_property
    def eave_slack_system_bot_token(self) -> str:
        value = self.get_secret("SLACK_SYSTEM_BOT_TOKEN")
        return value

    @property
    def eave_slack_app_id(self) -> str:
        k = "EAVE_SLACK_APP_ID"
        if v:= os.getenv(k):
            return v
        else:
            return self.gcp_metadata.get(k, "A04HD948UHE") # Fallback to production ID

    @cached_property
    def eave_slack_client_id(self) -> str:
        return self.get_secret("EAVE_SLACK_APP_CLIENT_ID")

    @cached_property
    def eave_slack_client_secret(self) -> str:
        return self.get_secret("EAVE_SLACK_APP_CLIENT_SECRET")

    @cached_property
    def eave_github_app_public_url(self) -> str:
        k = "EAVE_GITHUB_APP_PUBLIC_URL"
        if v:= os.getenv(k):
            return v
        else:
            return self.gcp_metadata.get(k, "https://github.com/apps/eave-fyi")

    @cached_property
    def gcp_metadata(self) -> dict[str,str]:
        project = _gcompute.ProjectsClient().get(
            _gcompute.GetProjectRequest(
                project=self.google_cloud_project,
                fields="commonInstanceMetadata",
            )
        )
        metadata = project.common_instance_metadata
        table: dict[str,str] = {}
        for item in metadata.items:
            table[item.key] = item.value

        return table

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
