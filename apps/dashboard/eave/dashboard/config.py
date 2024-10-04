from eave.stdlib.config import ConfigBase
from eave.stdlib.eave_origins import EaveApp


class _AppConfig(ConfigBase):
    eave_origin = EaveApp.eave_dashboard


DASHBOARD_APP_CONFIG = _AppConfig()
