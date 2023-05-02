import os
from functools import cached_property

import eave.stdlib.config


class AppConfig(eave.stdlib.config.EaveConfig):
    @cached_property
    def eave_slack_app_signing_secret(self) -> str:
        value: str = self.get_secret("EAVE_SLACK_APP_SIGNING_SECRET")
        return value

    @cached_property
    def eave_slack_app_socketmode_token(self) -> str:
        """
        This is for socketmode only
        """
        value: str = self.get_secret("EAVE_SLACK_APP_SOCKETMODE_TOKEN")
        return value


app_config = AppConfig()
