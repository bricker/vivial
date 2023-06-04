from functools import cached_property
import os

import eave.stdlib.config
from eave.stdlib.eave_origins import EaveOrigin

SLACK_EVENT_QUEUE_NAME = "slack-events-processor"
SLACK_EVENT_QUEUE_TARGET_PATH = "/_tasks/slack-events"
TASK_EXECUTION_COUNT_CONTEXT_KEY = "TASK_EXECUTION_COUNT_CONTEXT_KEY"


class AppConfig(eave.stdlib.config.EaveConfig):
    eave_origin = EaveOrigin.eave_slack_app

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

    @property
    def is_socketmode(self) -> bool:
        return os.getenv("SLACK_SOCKETMODE") is not None


app_config = AppConfig()
