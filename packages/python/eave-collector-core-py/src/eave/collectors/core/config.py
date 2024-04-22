import os

EAVE_API_BASE_URL = os.getenv("EAVE_API_BASE_PUBLIC", "https://api.eave.fyi")

# We don't call `os.getenv()` here so that the value can be read lazily.
EAVE_CREDENTIALS_ENV_KEY = "EAVE_CREDENTIALS"

class EaveConfigReader:
    def __init__(self) -> None:
        self.client_id = self._read_config_variable_or_exception("EAVE_CLIENT_ID")
        self.client_secret = self._read_config_variable_or_exception("EAVE_CLIENT_SECRET")

    def _read_config_variable_or_exception(self, key: str) -> str:
        value = os.getenv(key)
        if value is None:
            raise Exception(f"Unable to find required variable {key} in Eave config")
        return value
