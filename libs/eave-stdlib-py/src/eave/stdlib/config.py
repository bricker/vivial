import enum
import logging
import os
import re
import sys
from functools import cached_property
from typing import Optional
from urllib.parse import urlparse

import google.cloud.secretmanager
import google.cloud.client

from eave.stdlib.eave_origins import EaveApp


from . import checksum

GITHUB_EVENT_QUEUE_NAME = "github-events-processor"


class EaveEnvironment(enum.StrEnum):
    test = "test"
    development = "development"
    production = "production"


class ConfigBase:
    def preload(self) -> None:
        """
        This is meant to be used in a GAE warmup request to preload all of the remote configs.
        """
        for attrname, attrfunc in self.__class__.__dict__.items():
            if type(attrfunc) == cached_property:
                getattr(self, attrname)

    def reset_cached_properties(self) -> None:
        for attrname, attrfunc in self.__class__.__dict__.items():
            if type(attrfunc) == cached_property:
                try:
                    delattr(self, attrname)
                except AttributeError:
                    # Attribute doesn't exist, that's fine.
                    pass


class _EaveConfig(ConfigBase):
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
            case "test":
                return EaveEnvironment.test
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
        return os.getenv("EAVE_MONITORING_DISABLED") != "1"

    @property
    def analytics_enabled(self) -> bool:
        return os.getenv("EAVE_ANALYTICS_DISABLED") != "1"

    @property
    def google_cloud_project(self) -> str:
        return get_required_env("GOOGLE_CLOUD_PROJECT")

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
    def asset_base(self) -> str:
        return os.getenv("EAVE_ASSET_BASE", "/static")

    @property
    def eave_public_apps_base(self) -> str:
        return (
            os.getenv("EAVE_APPS_BASE_PUBLIC") or os.getenv("EAVE_APPS_BASE") or "https://apps.eave.fyi"  # deprecated
        )

    @property
    def eave_public_api_base(self) -> str:
        return self.eave_public_service_base(EaveApp.eave_api)

    @property
    def eave_public_www_base(self) -> str:
        return self.eave_public_service_base(EaveApp.eave_www)

    def eave_public_service_base(self, service: EaveApp) -> str:
        sname = service.value.upper()
        if v := os.getenv(f"{sname}_BASE_PUBLIC"):
            return v

        # EAVE_API_BASE, EAVE_WWW_BASE, and EAVE_APPS_BASE are deprecated.
        # Use EAVE_*_BASE_PUBLIC instead.
        # The `match` block here is mostly for the apps domain. The api and www cases shouldn't be reached
        # normally, but are here as fallbacks.
        match service:
            case EaveApp.eave_api:
                return os.getenv("EAVE_API_BASE") or "https://api.eave.fyi"  # deprecated
            case EaveApp.eave_www:
                return os.getenv("EAVE_WWW_BASE") or "https://www.eave.fyi"  # deprecated
            case _:
                return self.eave_public_apps_base

    def eave_internal_service_base(self, service: EaveApp) -> str:
        """
        This method gets the internal URL for the given service.
        It is a little messy because of the following:
        1. In development, the Public and Internal URLs are expected to be the same
        2. When running in AppEngine, the internal URLs have a different convention than the public URLs
        """

        sname = service.value.upper()
        if v := os.getenv(f"{sname}_BASE_INTERNAL"):
            return v

        if self.is_development:
            # In development, Internal and Public URLs are expected to be the same.
            match service:
                case EaveApp.eave_api:
                    return self.eave_public_api_base
                case EaveApp.eave_www:
                    return self.eave_public_www_base
                case _:
                    return self.eave_public_apps_base
        else:
            # In production (AppEngine), Internal and Public urls are expected to be different.
            # Internal AppEngine services eave have a specific base URL.
            # TODO: Remove hardcoded AppEngine URL
            # FIXME: Hardcoded region ID (uc)
            return "https://" f"{service.appengine_name}" "-dot-" f"{self.google_cloud_project}" ".uc.r.appspot.com"

    @property
    def eave_cookie_domain(self) -> str:
        if v := os.getenv("EAVE_COOKIE_DOMAIN"):
            return v

        parsed = urlparse(self.eave_public_www_base)
        host = parsed.hostname or "www.eave.fyi"
        return re.sub("www", "", host)

    @cached_property
    def redis_connection(self) -> Optional[tuple[str, int, str]]:
        key = "REDIS_HOST_PORT"
        value: str | None

        if self.is_development:
            # This secret should never be pulled from Google Cloud during development.
            value = os.getenv(key)
        else:
            try:
                value = get_secret(key)
            except Exception:
                value = None

        if not value:
            return None

        parts = value.split(":")
        if len(parts) == 3:
            host, port_, db = parts
            port = int(port_)
        elif len(parts) == 2:
            host, port_ = parts
            port = int(port_)
            db = "0"
        elif len(parts) == 1:
            host = parts[0]
            port = 6379
            db = "0"
        else:
            host = "localhost"
            port = 6379
            db = "0"

        return (host, port, db)

    @cached_property
    def redis_auth(self) -> Optional[str]:
        key = "REDIS_AUTH"

        if self.is_development:
            return os.getenv(key)
        else:
            try:
                return get_secret(key)
            except Exception:
                return None

    @cached_property
    def redis_tls_ca(self) -> Optional[str]:
        key = "REDIS_TLS_CA"

        if self.is_development:
            return os.getenv(key)
        else:
            try:
                return get_secret(key)
            except Exception:
                return None

    @cached_property
    def eave_openai_api_key(self) -> str:
        value = get_secret("OPENAI_API_KEY")
        return value

    @cached_property
    def eave_openai_api_org(self) -> str:
        value = get_secret("OPENAI_API_ORG")
        return value

    @cached_property
    def eave_slack_system_bot_token(self) -> str:
        value = get_secret("SLACK_SYSTEM_BOT_TOKEN")
        return value

    @cached_property
    def eave_slack_app_id(self) -> str:
        try:
            return get_secret("EAVE_SLACK_APP_ID")
        except Exception:
            # Fallback to the production ID, which won't change.
            return "A04HD948UHE"

    @cached_property
    def eave_slack_client_id(self) -> str:
        return get_secret("EAVE_SLACK_APP_CLIENT_ID")

    @cached_property
    def eave_slack_client_secret(self) -> str:
        return get_secret("EAVE_SLACK_APP_CLIENT_SECRET")

    @cached_property
    def eave_atlassian_app_client_id(self) -> str:
        return get_secret("EAVE_ATLASSIAN_APP_CLIENT_ID")

    @cached_property
    def eave_atlassian_app_client_secret(self) -> str:
        return get_secret("EAVE_ATLASSIAN_APP_CLIENT_SECRET")

    @cached_property
    def eave_github_app_public_url(self) -> str:
        return get_secret("EAVE_GITHUB_APP_PUBLIC_URL")


def get_secret(name: str) -> str:
    # Allow overrides from the environment
    if name in os.environ:
        return os.environ[name]

    secrets_client = google.cloud.secretmanager.SecretManagerServiceClient()
    fqname = secrets_client.secret_version_path(
        project=SHARED_CONFIG.google_cloud_project,
        secret=name,
        secret_version="latest",
    )
    response = secrets_client.access_secret_version(request={"name": fqname})
    data = response.payload.data
    data_crc32c = response.payload.data_crc32c

    checksum.validate_checksum_or_exception(data=data, checksum=data_crc32c)
    return data.decode("UTF-8")


def get_required_env(name: str) -> str:
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

SHARED_CONFIG = _EaveConfig()
