import os
from functools import cached_property

import eave.stdlib.config


class AppConfig(eave.stdlib.config.EaveConfig):
    @property
    def asset_base(self) -> str:
        return os.getenv("EAVE_ASSET_BASE", "/static")

    @cached_property
    def eave_web_session_encryption_key(self) -> str:
        key = "EAVE_WEB_SESSION_ENCRYPTION_KEY"
        if self.is_development:
            return os.getenv(key, "dev-encryption-key")
        else:
            return self.get_secret(key)


app_config = AppConfig()
