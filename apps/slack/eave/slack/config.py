import os
from functools import cached_property

import eave.stdlib.config


class AppConfig(eave.stdlib.config.EaveConfig):
    @property
    def eave_slack_app_id(self) -> str:
        return os.environ["EAVE_SLACK_APP_ID"]

    @cached_property
    def eave_slack_app_client_id(self) -> str:
        value = self.get_secret("EAVE_SLACK_APP_CLIENT_ID")
        assert value is not None
        return value

    @cached_property
    def eave_slack_app_client_secret(self) -> str:
        value = self.get_secret("EAVE_SLACK_APP_CLIENT_SECRET")
        assert value is not None
        return value

    @cached_property
    def eave_slack_app_signing_secret(self) -> str:
        value = self.get_secret("EAVE_SLACK_APP_SIGNING_SECRET")
        assert value is not None
        return value

    @cached_property
    def eave_slack_app_socketmode_token(self) -> str:
        """
        This is for socketmode only
        """
        value = self.get_secret("EAVE_SLACK_APP_SOCKETMODE_TOKEN")
        assert value is not None
        return value

    @cached_property
    def eave_slack_bot_token(self) -> str:
        """
        This is an oauth token.
        This is only needed while the app is being developed. Once it's published, this token will come from the
        OAuth2 flow, and each customer will have their own token.
        """
        value = self.get_secret("SLACK_BOT_TOKEN")
        assert value is not None
        return value


app_config = AppConfig()
