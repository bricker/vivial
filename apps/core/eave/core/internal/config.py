import json
from functools import cached_property
import os
from typing import Any, Mapping, Optional, Sequence

import eave.stdlib.config
from eave.stdlib.eave_origins import EaveOrigin
from eave.stdlib.exceptions import UnexpectedMissingValue
from eave.stdlib.logging import eaveLogger


class AppConfig(eave.stdlib.config.EaveConfig):
    @property
    def eave_origin(self) -> EaveOrigin:
        return EaveOrigin.eave_api

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
                eaveLogger.exception(f"Fetching {key} from secrets failed.")
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
        encoded = self.get_secret("EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_JSON")
        if not encoded:
            raise UnexpectedMissingValue("secret: EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_JSON")

        credentials: dict[str, Any] = json.loads(encoded)
        return credentials

    @cached_property
    def eave_google_oauth_client_id(self) -> str:
        credentials = self.eave_google_oauth_client_credentials
        client_id: str = credentials["web"]["client_id"]
        return client_id

    @property
    def eave_beta_prewhitelisted_emails(self) -> Sequence[str]:
        try:
            key = "EAVE_BETA_PREWHITELISTED_EMAILS_CSV"
            if self.is_development:
                value = os.getenv(key, "")
            else:
                value = self.get_secret(key)

            emails = list(map(str.strip, value.split(",")))
            return emails
        except Exception:
            eaveLogger.exception("Error while fetching beta whitelist")
            return []


app_config = AppConfig()
