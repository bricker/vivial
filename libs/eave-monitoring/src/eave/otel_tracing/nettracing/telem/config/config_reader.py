import os


class EaveConfigReader:
    def __init__(self):
        self.client_id = self._read_config_variable_or_exception("EAVE_CLIENT_ID")
        self.client_secret = self._read_config_variable_or_exception("EAVE_CLIENT_SECRET")

    def _read_config_variable_or_exception(self, key: str) -> str:
        value = os.getenv(key)
        if value is None:
            raise Exception(f"Unable to find required variable {key} in Eave config")
        return value
