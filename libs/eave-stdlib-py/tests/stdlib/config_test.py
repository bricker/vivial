import logging
from datetime import UTC

from eave.stdlib.config import SHARED_CONFIG

from .base import StdlibBaseTestCase


class ConfigTest(StdlibBaseTestCase):
    async def test_eave_base_url_public_with_env(self):
        self.patch_env({"EAVE_BASE_URL_PUBLIC": "https://finny.com:9090"})
        assert SHARED_CONFIG.eave_base_url_public == "https://finny.com:9090"
        assert SHARED_CONFIG.eave_hostname_public == "finny.com"
        assert SHARED_CONFIG.eave_netloc_public == "finny.com:9090"

    async def test_eave_base_url_public_default(self):
        self.patch_env({"EAVE_BASE_URL_PUBLIC": None})
        assert SHARED_CONFIG.eave_base_url_public == "https://vivialapp.com"
        assert SHARED_CONFIG.eave_hostname_public == "vivialapp.com"
        assert SHARED_CONFIG.eave_netloc_public == "vivialapp.com"

    async def test_eave_base_url_internal_with_env(self):
        self.patch_env({"EAVE_BASE_URL_INTERNAL": "http://internal.vivialapp.com"})
        assert SHARED_CONFIG.eave_base_url_internal == "http://internal.vivialapp.com"

    async def test_eave_base_url_internal_default(self):
        self.patch_env({"EAVE_BASE_URL_INTERNAL": None})
        assert SHARED_CONFIG.eave_base_url_internal == "http://eave.svc.cluster.local"

    async def test_eave_api_base_url_public_with_env(self):
        url = "https://coreapi.finny.com"
        self.patch_env({"EAVE_API_BASE_URL_PUBLIC": url})
        assert SHARED_CONFIG.eave_api_base_url_public == url
        assert SHARED_CONFIG.eave_api_hostname_public == "coreapi.finny.com"

    async def test_eave_api_base_url_public_fallback(self):
        self.patch_env(
            {
                "EAVE_API_BASE_URL_PUBLIC": None,
                "EAVE_BASE_URL_PUBLIC": "https://finny.com:8080",
            }
        )
        assert SHARED_CONFIG.eave_api_base_url_public == "https://api.finny.com:8080"
        assert SHARED_CONFIG.eave_api_hostname_public == "api.finny.com"

    async def test_eave_api_base_url_public_fallback_noport(self):
        self.patch_env(
            {
                "EAVE_API_BASE_URL_PUBLIC": None,
                "EAVE_BASE_URL_PUBLIC": "https://finny.com",
            }
        )
        assert SHARED_CONFIG.eave_api_base_url_public == "https://api.finny.com"

    async def test_eave_api_base_url_public_default(self):
        self.patch_env(
            {
                "EAVE_API_BASE_URL_PUBLIC": None,
                "EAVE_BASE_URL_PUBLIC": None,
            }
        )
        assert SHARED_CONFIG.eave_api_base_url_public == "https://api.vivialapp.com"

    async def test_eave_api_base_url_internal_with_env(self):
        url = self.anyurl()
        self.patch_env({"EAVE_API_BASE_URL_INTERNAL": url})
        assert SHARED_CONFIG.eave_api_base_url_internal == url

    async def test_eave_api_base_url_internal_fallback(self):
        self.patch_env(
            {
                "EAVE_API_BASE_URL_INTERNAL": None,
                "EAVE_BASE_URL_INTERNAL": "https://internal.finny.com",
            }
        )
        assert SHARED_CONFIG.eave_api_base_url_internal == "https://core-api.internal.finny.com"

    async def test_eave_api_base_url_internal_default(self):
        self.patch_env(
            {
                "EAVE_API_BASE_URL_INTERNAL": None,
                "EAVE_BASE_URL_INTERNAL": None,
            }
        )
        assert SHARED_CONFIG.eave_api_base_url_internal == "http://core-api.eave.svc.cluster.local"

    async def test_eave_dashboard_base_url_public_with_env(self):
        url = self.anyurl()
        self.patch_env({"EAVE_DASHBOARD_BASE_URL_PUBLIC": url})
        assert SHARED_CONFIG.eave_dashboard_base_url_public == url

    async def test_eave_dashboard_base_url_public_fallback(self):
        self.patch_env(
            {
                "EAVE_DASHBOARD_BASE_URL_PUBLIC": None,
                "EAVE_BASE_URL_PUBLIC": "https://finny.com",
            }
        )
        assert SHARED_CONFIG.eave_dashboard_base_url_public == "https://www.finny.com"

    async def test_eave_dashboard_base_url_public_default(self):
        self.patch_env(
            {
                "EAVE_DASHBOARD_BASE_URL_PUBLIC": None,
                "EAVE_BASE_URL_PUBLIC": None,
            }
        )
        assert SHARED_CONFIG.eave_dashboard_base_url_public == "https://www.vivialapp.com"

    async def test_is_production(self):
        self.patch_env({"EAVE_ENV": "production"})
        assert SHARED_CONFIG.eave_env == "production"
        assert SHARED_CONFIG.is_production is True
        assert SHARED_CONFIG.is_staging is False
        assert SHARED_CONFIG.is_development is False
        assert SHARED_CONFIG.is_test is False
        assert SHARED_CONFIG.raise_app_exceptions is False

    async def test_is_staging(self):
        self.patch_env({"EAVE_ENV": "staging"})
        assert SHARED_CONFIG.eave_env == "staging"
        assert SHARED_CONFIG.is_production is False
        assert SHARED_CONFIG.is_staging is True
        assert SHARED_CONFIG.is_development is False
        assert SHARED_CONFIG.is_test is False
        assert SHARED_CONFIG.raise_app_exceptions is False

    async def test_is_development(self):
        self.patch_env({"EAVE_ENV": "development"})
        assert SHARED_CONFIG.eave_env == "development"
        assert SHARED_CONFIG.is_production is False
        assert SHARED_CONFIG.is_staging is False
        assert SHARED_CONFIG.is_development is True
        assert SHARED_CONFIG.is_test is False
        assert SHARED_CONFIG.raise_app_exceptions is True

    async def test_is_test(self):
        self.patch_env({"EAVE_ENV": "test"})
        assert SHARED_CONFIG.eave_env == "test"
        assert SHARED_CONFIG.is_production is False
        assert SHARED_CONFIG.is_staging is False
        assert SHARED_CONFIG.is_development is False
        assert SHARED_CONFIG.is_test is True
        assert SHARED_CONFIG.raise_app_exceptions is True

    async def test_unknown_env(self):
        self.patch_env({"EAVE_ENV": self.anystr()})
        assert SHARED_CONFIG.eave_env == "production"
        assert SHARED_CONFIG.is_production is True
        assert SHARED_CONFIG.is_staging is False
        assert SHARED_CONFIG.is_development is False
        assert SHARED_CONFIG.is_test is False
        assert SHARED_CONFIG.raise_app_exceptions is False

    async def test_monitoring_disabled(self):
        self.patch_env({"EAVE_MONITORING_DISABLED": "1"})
        assert SHARED_CONFIG.monitoring_enabled is False

    async def test_monitoring_enabled(self):
        self.patch_env({"EAVE_MONITORING_DISABLED": None})
        assert SHARED_CONFIG.monitoring_enabled is True

    async def test_analytics_disabled(self):
        self.patch_env({"EAVE_ANALYTICS_DISABLED": "1"})
        assert SHARED_CONFIG.analytics_enabled is False

    async def test_analytics_enabled(self):
        self.patch_env({"EAVE_ANALYTICS_DISABLED": None})
        assert SHARED_CONFIG.analytics_enabled is True

    async def test_log_level_with_env(self):
        self.patch_env({"LOG_LEVEL": "WARNING"})
        assert SHARED_CONFIG.log_level == logging.WARNING

    async def test_log_level_default(self):
        self.patch_env({"LOG_LEVEL": None})
        assert SHARED_CONFIG.log_level == logging.INFO

    async def test_log_level_unknown_value(self):
        self.patch_env({"LOG_LEVEL": self.anystr()})
        assert SHARED_CONFIG.log_level == logging.INFO

    async def test_app_service_with_env(self):
        v = self.anystr()
        self.patch_env({"GAE_SERVICE": v})
        assert SHARED_CONFIG.app_service == v

    async def test_app_service_default(self):
        self.patch_env({"GAE_SERVICE": None})
        assert SHARED_CONFIG.app_service == "unknown"

    async def test_app_version_with_env(self):
        v = self.anystr()
        self.patch_env({"GAE_VERSION": v})
        assert SHARED_CONFIG.app_version == v

    async def test_app_version_default(self):
        self.patch_env({"GAE_VERSION": None})
        assert SHARED_CONFIG.app_version == "unknown"

    async def test_release_date_with_env(self):
        v = self.anystr()
        self.patch_env({"GAE_RELEASE_DATE": v})
        assert SHARED_CONFIG.release_date == v

    async def test_release_date_default(self):
        self.patch_env({"GAE_RELEASE_DATE": None})
        assert SHARED_CONFIG.release_date == "unknown"

    async def test_release_timestamp_with_valid_iso(self):
        v = self.anydatetime("release_date", past=True).isoformat()
        self.patch_env({"GAE_RELEASE_DATE": v})
        assert SHARED_CONFIG.release_timestamp == self.getdatetime("release_date").timestamp()

    async def test_release_timestamp_with_valid_iso_with_offset(self):
        v = self.anydatetime("release_date", past=True, tz=UTC).isoformat()
        self.patch_env({"GAE_RELEASE_DATE": v})
        assert SHARED_CONFIG.release_timestamp == self.getdatetime("release_date").timestamp()

    async def test_release_timestamp_with_valid_iso_with_no_offset(self):
        v = self.anydatetime("release_date", past=True, tz=None).isoformat()
        self.patch_env({"GAE_RELEASE_DATE": v})
        assert SHARED_CONFIG.release_timestamp == self.getdatetime("release_date").timestamp()

    async def test_release_timestamp_with_valid_iso_with_micros(self):
        v = self.anydatetime("release_date", past=True, resolution="seconds").isoformat(timespec="microseconds")
        self.patch_env({"GAE_RELEASE_DATE": v})
        assert SHARED_CONFIG.release_timestamp == self.getdatetime("release_date").timestamp()

    async def test_release_timestamp_with_valid_iso_with_millis(self):
        v = self.anydatetime("release_date", past=True, resolution="seconds").isoformat(timespec="milliseconds")
        self.patch_env({"GAE_RELEASE_DATE": v})
        assert SHARED_CONFIG.release_timestamp == self.getdatetime("release_date").timestamp()

    async def test_release_timestamp_with_valid_iso_with_seconds(self):
        v = self.anydatetime("release_date", future=True, resolution="seconds").isoformat(timespec="seconds")
        self.patch_env({"GAE_RELEASE_DATE": v})
        assert SHARED_CONFIG.release_timestamp == self.getdatetime("release_date").timestamp()

    async def test_release_timestamp_with_missing_release_date(self):
        self.patch_env({"GAE_RELEASE_DATE": None})
        assert SHARED_CONFIG.release_timestamp is None

    async def test_release_timestamp_with_missing_invalid_iso_format(self):
        self.patch_env({"GAE_RELEASE_DATE": self.anystr()})
        assert SHARED_CONFIG.release_timestamp is None

    async def test_asset_base_with_env(self):
        v = self.anypath()
        self.patch_env({"EAVE_ASSET_BASE": v})
        assert SHARED_CONFIG.asset_base == v

    async def test_asset_base_default(self):
        self.patch_env({"EAVE_ASSET_BASE": None})
        assert SHARED_CONFIG.asset_base == "/static"

    async def test_google_cloud_project_with_env(self):
        self.patch_env(
            {"GOOGLE_CLOUD_PROJECT": "google"}
        )  # not using anystr() here to avoid accidentally hitting someone else's project
        assert SHARED_CONFIG.google_cloud_project == "google"

    async def test_google_cloud_project_not_set(self):
        self.patch_env({"GOOGLE_CLOUD_PROJECT": None})
        self.assertRaises(KeyError, lambda: SHARED_CONFIG.google_cloud_project)
