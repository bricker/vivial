import base64
import json
from functools import cached_property
import os
from typing import Any, Mapping, Optional, Sequence

import eave.stdlib.config
from eave.stdlib import logger

class AppConfig(eave.stdlib.config.EaveConfig):
    @cached_property
    def db_host(self) -> str:
        key = "EAVE_DB_HOST"
        if self.is_development:
            return self.get_required_env(key)
        else:
            return self.get_secret(key)

    @cached_property
    def db_user(self) -> str:
        key = "EAVE_DB_USER"
        if self.is_development:
            return self.get_required_env(key)
        else:
            return self.get_secret(key)

    @cached_property
    def db_pass(self) -> Optional[str]:
        key = "EAVE_DB_PASS"
        if self.is_development:
            value = os.getenv(key)
            # Treat empty strings as None
            return None if not value else value
        else:
            try:
                return self.get_secret(key)
            except Exception:
                logger.exception(f"Fetching {key} from secrets failed.")
                return None

    @cached_property
    def db_name(self) -> str:
        key = "EAVE_DB_NAME"
        if self.is_development:
            return self.get_required_env(key)
        else:
            return self.get_secret(key)

    @cached_property
    def eave_google_oauth_client_credentials(self) -> Mapping[str, Any]:
        encoded = self.get_secret("EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_B64")
        assert encoded is not None
        bytes = base64.b64decode(encoded)
        credentials: dict[str, Any] = json.loads(bytes)
        return credentials

    @cached_property
    def eave_google_oauth_client_id(self) -> str:
        credentials = self.eave_google_oauth_client_credentials
        client_id: str = credentials["web"]["client_id"]
        return client_id

    @property
    def eave_beta_prewhitelisted_emails(self) -> Sequence[str]:
        try:
            value: str = self.get_secret("EAVE_BETA_PREWHITELISTED_EMAILS_CSV")
            emails = list(map(str.strip, value.split(",")))
            return emails
        except Exception:
            return []


app_config = AppConfig()
