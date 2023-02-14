import os

from dotenv import load_dotenv

load_dotenv(".env.test")

import eave.internal.settings as _settings

_settings.APP_SETTINGS = _settings.Settings()
