import datetime
import enum
import logging
import os
from functools import cached_property
from urllib.parse import urlparse

import google.cloud.client
import google.cloud.secretmanager

from . import checksum

GITHUB_EVENT_QUEUE_NAME = "github-events-processor"


class EaveEnvironment(enum.StrEnum):
    test = "test"
    development = "development"
    staging = "staging"
    production = "production"


class ConfigBase:
    def preload(self) -> None:
        """
        This is meant to be used in a GAE warmup request to preload all of the remote configs.
        """
        for attrname, attrfunc in self.__class__.__dict__.items():
            if isinstance(attrfunc, cached_property):
                getattr(self, attrname)

    def reset_cached_properties(self) -> None:
        for attrname, attrfunc in self.__class__.__dict__.items():
            if isinstance(attrfunc, cached_property):
                try:
                    delattr(self, attrname)
                except AttributeError:
                    # Attribute doesn't exist, that's fine.
                    pass


class _EaveConfig(ConfigBase):
    @property
    def log_level(self) -> int:
        level = os.getenv("LOG_LEVEL") or "INFO"
        mapping = logging.getLevelNamesMapping()
        return mapping.get(level.upper(), logging.INFO)

    @property
    def eave_env(self) -> EaveEnvironment:
        strenv = os.getenv("EAVE_ENV") or "production"
        match strenv:
            case "test":
                return EaveEnvironment.test
            case "development":
                return EaveEnvironment.development
            case "staging":
                return EaveEnvironment.staging
            case "production":
                return EaveEnvironment.production
            case _:
                return EaveEnvironment.production

    @property
    def is_production(self) -> bool:
        return self.eave_env is EaveEnvironment.production

    @property
    def is_staging(self) -> bool:
        return self.eave_env is EaveEnvironment.staging

    @property
    def is_development(self) -> bool:
        return self.eave_env is EaveEnvironment.development

    @property
    def is_test(self) -> bool:
        return self.eave_env is EaveEnvironment.test

    @property
    def is_local(self) -> bool:
        return self.is_development or self.is_test

    @property
    def raise_app_exceptions(self) -> bool:
        """
        This is intended for use during development.
        When set to True, unhandled exceptions raised during the request won't be handled.
        In production (i.e. when this flag is False), unhandled exceptions are caught, logged, and return a 500.
        """
        return self.is_local

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
        return os.getenv("GAE_SERVICE") or "unknown"

    @property
    def app_version(self) -> str:
        return os.getenv("GAE_VERSION") or "unknown"

    @property
    def release_date(self) -> str:
        return os.getenv("GAE_RELEASE_DATE") or "unknown"

    @property
    def release_timestamp(self) -> float | None:
        isodate = self.release_date
        try:
            return datetime.datetime.fromisoformat(isodate).timestamp()
        except ValueError:
            return None

    @property
    def asset_base(self) -> str:
        return os.getenv("EAVE_ASSET_BASE", "/static")

    ## Base URLs

    @property
    def eave_base_url_public(self) -> str:
        return os.getenv("EAVE_BASE_URL_PUBLIC") or "https://eave.fyi"

    @property
    def eave_base_url_internal(self) -> str:
        return os.getenv("EAVE_BASE_URL_INTERNAL") or "http://eave.svc.cluster.local"

    @property
    def eave_hostname_public(self) -> str:
        return urlparse(self.eave_base_url_public).hostname or "eave.fyi"

    @property
    def eave_netloc_public(self) -> str:
        return urlparse(self.eave_base_url_public).netloc or self.eave_hostname_public

    @property
    def eave_api_base_url_public(self) -> str:
        return os.getenv("EAVE_API_BASE_URL_PUBLIC") or _prefix_hostname(url=self.eave_base_url_public, prefix="api.")

    @property
    def eave_api_base_url_internal(self) -> str:
        return os.getenv("EAVE_API_BASE_URL_INTERNAL") or _prefix_hostname(
            url=self.eave_base_url_internal, prefix="core-api."
        )

    @property
    def eave_dashboard_base_url_public(self) -> str:
        return os.getenv("EAVE_DASHBOARD_BASE_URL_PUBLIC") or _prefix_hostname(
            url=self.eave_base_url_public, prefix="dashboard."
        )

    @property
    def eave_cookie_domain(self) -> str:
        return self.eave_hostname_public

    @property
    def jws_signing_key_version_path(self) -> str:
        return os.getenv(
            "JWS_SIGNING_KEY_VERSION_PATH",
            f"projects/{self.google_cloud_project}/locations/global/keyRings/primary/cryptoKeys/jws-signing-key/cryptoKeyVersions/1",
        )

    @cached_property
    def redis_connection(self) -> tuple[str, int, str] | None:
        key = "REDIS_HOST_PORT"
        value: str | None

        if self.is_local:
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
    def redis_auth(self) -> str | None:
        key = "REDIS_AUTH"

        if self.is_local:
            return os.getenv(key)
        else:
            try:
                return get_secret(key)
            except Exception:
                return None

    @cached_property
    def redis_tls_ca(self) -> str | None:
        key = "REDIS_TLS_CA"

        if self.is_local:
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
    def eave_slack_system_bot_token(self) -> str:
        value = get_secret("SLACK_SYSTEM_BOT_TOKEN")
        return value

    @cached_property
    def eave_slack_signups_channel_id(self) -> str | None:
        value = os.getenv("EAVE_SLACK_SIGNUPS_CHANNEL_ID")
        return value

    @cached_property
    def segment_website_write_key(self) -> str:
        value = os.getenv("SEGMENT_WEBSITE_WRITE_KEY")
        assert value is not None, "Segment website write key not set"
        return value


def get_secret(name: str) -> str:
    # Allow overrides from the environment
    if (envval := os.environ.get(name)) and envval != "(not set)":
        return envval

    secrets_client = google.cloud.secretmanager.SecretManagerServiceClient()
    fqname = secrets_client.secret_version_path(
        project=SHARED_CONFIG.google_cloud_project,
        secret=name,
        secret_version="latest",  # noqa: S106
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


def _prefix_hostname(url: str, prefix: str) -> str:
    p = urlparse(url)
    p = p._replace(netloc=f"{prefix}{p.netloc}")
    return p.geturl()


SHARED_CONFIG = _EaveConfig()
