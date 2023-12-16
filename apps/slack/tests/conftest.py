# ruff: noqa: E402

import os

os.environ["EAVE_ENV"] = "test"

from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

load_standard_dotenv_files()


import eave.stdlib.time

eave.stdlib.time.set_utc()
