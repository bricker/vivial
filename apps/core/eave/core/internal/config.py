import base64
import json
from functools import cached_property
from typing import Any, Mapping, Optional, Sequence

import eave.stdlib.config


class AppConfig(eave.stdlib.config.EaveConfig):
    @cached_property
    def cloudsql_connection_string(self) -> str:
        value = self.get_secret("EAVE_CLOUDSQL_CONNECTION_STRING")
        return value

    @cached_property
    def db_host(self) -> Optional[str]:
        value = self.get_secret("EAVE_DB_HOST")
        return value

    @cached_property
    def db_user(self) -> Optional[str]:
        value: str = self.get_secret("EAVE_DB_USER")
        return value

    @cached_property
    def db_pass(self) -> Optional[str]:
        value: str = self.get_secret("EAVE_DB_PASS")
        if not value:  # Treat empty string as no password
            return None
        return value

    @cached_property
    def db_name(self) -> str:
        value: str = self.get_secret("EAVE_DB_NAME")
        return value

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
