import eave.stdlib.config
from eave.stdlib.eave_origins import EaveOrigin

class AppConfig(eave.stdlib.config.EaveConfig):
    eave_origin = EaveOrigin.{{origin_name}}


app_config = AppConfig()
