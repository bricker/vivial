import os

from eave.stdlib.config import SHARED_CONFIG, ConfigBase, EaveEnvironment


class _AppConfig(ConfigBase):
    pass


ADMIN_APP_CONFIG = _AppConfig()
