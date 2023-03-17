import base64
import json
import os
from functools import cached_property
from typing import Any, Mapping, Optional

import google_crc32c
from google.cloud import secretmanager

import eave_stdlib.config

class AppConfig(eave_stdlib.config.EaveConfig):
    @property
    def eave_slack_app_id(self) -> str:
        return os.environ["EAVE_SLACK_APP_ID"]

    @cached_property
    def eave_slack_app_token(self) -> Optional[str]:
        return eave_stdlib.config.get_secret("SLACK_APP_TOKEN")

    @cached_property
    def eave_slack_bot_signing_secret(self) -> Optional[str]:
        return eave_stdlib.config.get_secret("SLACK_SIGNING_SECRET")

app_config = AppConfig()