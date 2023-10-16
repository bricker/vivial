import os

import eave.stdlib.config
from eave.stdlib.eave_origins import EaveApp


class AppConfig(eave.stdlib.config.EaveConfig):
    eave_origin = EaveApp.eave_www

    @property
    def asset_base(self) -> str:
        return os.getenv("EAVE_ASSET_BASE", "/static")


app_config = AppConfig()
