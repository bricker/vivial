from functools import cached_property

from eave.stdlib.config import ConfigBase, get_required_env


class _AppConfig(ConfigBase):
    @cached_property
    def segment_website_write_key(self) -> str:
        return get_required_env("SEGMENT_WEBSITE_WRITE_KEY")


DASHBOARD_APP_CONFIG = _AppConfig()
