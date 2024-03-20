# ruff: noqa: E402

import os


os.environ["EAVE_ENV"] = "test"

from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

load_standard_dotenv_files()

import eave.stdlib.time

eave.stdlib.time.set_utc()

from eave.stdlib.config import SHARED_CONFIG

# Attempt to prevent accidentally running tests against the production environment.
assert SHARED_CONFIG.google_cloud_project != "eave-production"
assert SHARED_CONFIG.eave_env == "test"
