from functools import cached_property
import os
from eave.stdlib.config import ConfigBase, get_secret

from eave.stdlib.eave_origins import EaveApp

SLACK_EVENT_QUEUE_NAME = "slack-events-processor"
TASK_EXECUTION_COUNT_CONTEXT_KEY = "TASK_EXECUTION_COUNT"
EAVE_CTX_KEY = "EAVE_CTX_KEY"


class _AppConfig(ConfigBase):
    eave_origin = EaveApp.eave_slack_app

    @cached_property
    def eave_slack_app_signing_secret(self) -> str:
        value: str = get_secret("EAVE_SLACK_APP_SIGNING_SECRET")
        return value

    @cached_property
    def eave_slack_app_socketmode_token(self) -> str:
        """
        This is for socketmode only
        """
        value: str = get_secret("EAVE_SLACK_APP_SOCKETMODE_TOKEN")
        return value

    @property
    def is_socketmode(self) -> bool:
        return os.getenv("SLACK_SOCKETMODE") is not None


SLACK_APP_CONFIG = _AppConfig()
