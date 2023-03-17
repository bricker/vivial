import base64
from functools import cached_property
import json
import os
from typing import Any, Mapping, Optional
import eave_stdlib.config

class AppConfig(eave_stdlib.config.EaveConfig):
    @property
    def db_connection_string(self) -> Optional[str]:
        return os.getenv("EAVE_DB_CONNECTION_STRING")

    @property
    def db_driver(self) -> str:
        return os.getenv("EAVE_DB_DRIVER", "postgresql+asyncpg")

    @property
    def db_name(self) -> str:
        return os.getenv("EAVE_DB_NAME", "eave")

    @property
    def db_host(self) -> str:
        value = os.getenv("EAVE_DB_HOST")
        assert value is not None
        return value

    @property
    def db_port(self) -> Optional[int]:
        port = os.getenv("EAVE_DB_PORT")
        if port is None:
            return None
        return int(port)

    @cached_property
    def db_user(self) -> str:
        value = eave_stdlib.config.get_secret("DB_USER")
        assert value is not None
        return value

    @cached_property
    def db_pass(self) -> str:
        value = self.get_secret("DB_PASS")
        assert value is not None
        return value

    @cached_property
    def eave_google_oauth_client_credentials(self) -> Mapping[str, Any]:
        encoded = eave_stdlib.config.get_secret("EAVE_GOOGLE_OAUTH_CLIENT_CREDENTIALS_B64")
        assert encoded is not None
        bytes = base64.b64decode(encoded)
        credentials: dict[str, Any] = json.loads(bytes)
        return credentials

    @cached_property
    def eave_google_oauth_client_id(self) -> str:
        client_id: str = self.eave_google_oauth_client_credentials["web"]["client_id"]
        return client_id

app_config = AppConfig()
