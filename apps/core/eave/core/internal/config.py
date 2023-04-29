import base64
import json
import os
from functools import cached_property
from typing import Any, List, Mapping, Optional

import eave.stdlib.config


class AppConfig(eave.stdlib.config.EaveConfig):
    @property
    def db_host(self) -> Optional[str]:
        value = os.getenv("EAVE_DB_HOST")
        return value

    @cached_property
    def db_user(self) -> Optional[str]:
        try:
            value: str = self.get_secret("EAVE_DB_USER")
            return value
        except AssertionError:
            return None

    @property
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
    def eave_beta_prewhitelisted_emails(self) -> List[str]:
        try:
            value: str = self.get_secret("EAVE_BETA_PREWHITELISTED_EMAILS_CSV")
            emails = list(map(str.strip, value.split(",")))
            return emails
        except:
            return []

app_config = AppConfig()
