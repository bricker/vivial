import os
from functools import cached_property

from eave.stdlib.config import ConfigBase, get_required_env


class _AppConfig(ConfigBase):
    @cached_property
    def segment_website_write_key(self) -> str:
        return get_required_env("SEGMENT_WEBSITE_WRITE_KEY")

    @cached_property
    def stripe_publishable_key(self) -> str:
        return get_required_env("STRIPE_PUBLISHABLE_KEY")

    @property
    def apple_domain_verification_code(self) -> str:
        return os.getenv("EAVE_WWW_APPLE_DOMAIN_VERIFICATION_CODE", "")

    @property
    def datadog_application_id(self) -> str:
        return os.getenv("EAVE_WWW_DATADOG_APPLICATION_ID", "")

    @property
    def datadog_client_token(self) -> str:
        return os.getenv("EAVE_WWW_DATADOG_CLIENT_TOKEN", "")


DASHBOARD_APP_CONFIG = _AppConfig()
