import os
from functools import cached_property

import eave.stdlib.config


class AppConfig(eave.stdlib.config.EaveConfig):
    @property
    def eave_slack_app_id(self) -> str:
        return os.environ["EAVE_SLACK_APP_ID"]

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

    @cached_property
    def eave_slack_bot_token(self) -> str:
        """
        This is an oauth token.
        This is only needed while the app is being developed. Once it's published, this token will come from the
        OAuth2 flow, and each customer will have their own token.
        """
        value: str = self.get_secret("SLACK_BOT_TOKEN")
        return value


app_config = AppConfig()
