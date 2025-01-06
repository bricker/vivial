import os

from eave.stdlib.config import SHARED_CONFIG, ConfigBase, EaveEnvironment, get_required_env


class _AppConfig(ConfigBase):
    @property
    def root_iap_enabled(self) -> bool:
        return os.getenv("EAVE_WWW_ROOT_IAP_ENABLED") != "0"

    @property
    def iap_jwt_aud(self) -> str | None:
        if self.root_iap_enabled:
            return get_required_env("EAVE_WWW_IAP_JWT_AUD")
        else:
            return None

    @property
    def segment_write_key(self) -> str:
        match SHARED_CONFIG.eave_env:
            case EaveEnvironment.test | EaveEnvironment.development:
                return "jAo8uNKdDt81A0PL3S6oASxAHZ7BTWYI"  # Not Sensitive
            case EaveEnvironment.staging:
                return "dO1quf6odO8UQ5lLiJPHu0SFjy6OImu1"  # Not Sensitive
            case EaveEnvironment.production:
                return "GcB5ShHbFcZZKIGTlvanJerSyKp9yJNv"  # Not Sensitive

    @property
    def apple_domain_verification_code(self) -> str:
        return os.getenv("EAVE_WWW_APPLE_DOMAIN_VERIFICATION_CODE", "")

    @property
    def datadog_application_id(self) -> str:
        return "1e7d90fe-10f6-408a-802f-e15b49efb50f"  # Not sensitive

    @property
    def datadog_client_token(self) -> str:
        return "pub3982d7524ad11a2faa827f44fe6d76f3"  # Not sensitive


DASHBOARD_APP_CONFIG = _AppConfig()
