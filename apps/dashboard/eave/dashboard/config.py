from functools import cached_property
import os

from eave.stdlib.config import ConfigBase, get_required_env


class _AppConfig(ConfigBase):
    @cached_property
    def segment_website_write_key(self) -> str:
        return get_required_env("SEGMENT_WEBSITE_WRITE_KEY")

    @cached_property
    def stripe_publishable_key(self) -> str:
        return get_required_env("STRIPE_PUBLISHABLE_KEY")

    def apple_domain_verification_code(self) -> str:
        return os.getenv("EAVE_WWW_APPLE_DOMAIN_VERIFICATION_CODE", "")


DASHBOARD_APP_CONFIG = _AppConfig()
