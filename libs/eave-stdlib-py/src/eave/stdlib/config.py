import enum
import logging
import os
import re
import sys
from functools import cached_property
from typing import Optional, Self
from urllib.parse import urlparse

import google.cloud.secretmanager
import google.cloud.runtimeconfig
import google.cloud.client

from eave.stdlib.eave_origins import EaveService


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
        return os.getenv("EAVE_MONITORING_DISABLED") is None

    @property
    def analytics_enabled(self) -> bool:
        return os.getenv("EAVE_ANALYTICS_DISABLED") is None

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
    def eave_public_apps_base(self) -> str:
        return (
            os.getenv("EAVE_PUBLIC_APPS_BASE")
            or os.getenv("EAVE_APPS_BASE") # deprecated
            or "https://apps.eave.fyi"
        )

    @property
    def eave_public_api_base(self) -> str:
        return self.eave_public_service_base(EaveService.api)

    @property
    def eave_public_www_base(self) -> str:
        return self.eave_public_service_base(EaveService.www)

    def eave_public_service_base(self, service: EaveService) -> str:
        sname = service.value.upper()
        if v := os.getenv(f"EAVE_PUBLIC_{sname}_BASE"):
            return v

        # EAVE_API_BASE, EAVE_WWW_BASE, and EAVE_APPS_BASE are deprecated.
        # Use EAVE_PUBLIC_*_BASE instead.
        # The `match` block here is mostly for the apps domain. The api and www cases shouldn't be reached
        # normally, but are here as fallbacks.
        match service:
            case EaveService.api:
                return (
                    os.getenv("EAVE_API_BASE") # deprecated
                    or "https://api.eave.fyi"
                )
            case EaveService.www:
                return (
                    os.getenv("EAVE_WWW_BASE") # deprecated
                    or "https://www.eave.fyi"
                )
            case _:
                return self.eave_public_apps_base

    def eave_internal_service_base(self, service: EaveService) -> str:
        """
        This method gets the internal URL for the given service.
        It is a little messy because of the following:
        1. In development, the Public and Internal URLs are expected to be the same
        2. When running in AppEngine, the internal URLs have a different convention than the public URLs
        """

        sname = service.value.upper()
        if v := os.getenv(f"EAVE_INTERNAL_{sname}_BASE"):
            return v

        if self.is_development:
            # In development, Internal and Public URLs are expected to be the same.
            match service:
                case EaveService.api:
                    return self.eave_public_api_base
                case EaveService.www:
                    return self.eave_public_www_base
                case _:
                    return self.eave_public_apps_base
        else:
            # In production (AppEngine), Internal and Public urls are expected to be different.
            # Internal AppEngine services eave have a specific base URL.
            # FIXME: Hardcoded region ID (uc)
            return (
                "https://"
                f"{service.value}"
                "-dot-"
                f"{self.google_cloud_project}"
                ".uc.r.appspot.com"
            )

    @property
    def eave_cookie_domain(self) -> str:
        if (v := os.getenv("EAVE_COOKIE_DOMAIN")):
            return v

        parsed = urlparse(self.eave_public_www_base)
        host = parsed.hostname or "www.eave.fyi"
        return re.sub("www", "", host)

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
    def eave_openai_api_org(self) -> str:
        value = self.get_secret("OPENAI_API_ORG")
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
