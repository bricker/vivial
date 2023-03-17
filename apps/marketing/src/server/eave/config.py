import base64
import json
import os
from functools import cached_property
from typing import Any, Mapping, Optional

import eave_stdlib.config


class AppConfig(eave_stdlib.config.EaveConfig):
    @property
    def app_env(self) -> str:
        if os.getenv("FLASK_DEBUG") is not None:
            return "development"
        else:
            return "production"

    @property
    def analytics_enabled(self) -> bool:
        return os.getenv("EAVE_ANALYTICS_ENABLED") is not None

    @property
    def asset_base(self) -> str:
        return os.getenv("EAVE_ASSET_BASE", "/static")

    @cached_property
    def eave_web_session_encryption_key(self) -> str:
        key = eave_stdlib.config.get_secret("EAVE_WEB_SESSION_ENCRYPTION_KEY")
        assert key is not None
        return key

app_config = AppConfig()
