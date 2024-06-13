import os

from eave.stdlib.config import ConfigBase
from eave.stdlib.eave_origins import EaveApp


class _AppConfig(ConfigBase):
    eave_origin = EaveApp.eave_dashboard

    @property
    def collector_asset_base(self) -> str:
        return os.getenv("COLLECTOR_ASSET_BASE", "https://storage.googleapis.com/cdn.eave.fyi")

    @property
    def eave_client_id(self) -> str:
        return os.getenv("EAVE_CLIENT_ID", "")


DASHBOARD_APP_CONFIG = _AppConfig()
