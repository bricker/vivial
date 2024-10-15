import sys

from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

sys.path.append(".")

load_standard_dotenv_files()

# ruff: noqa: E402

# Import some common modules
import asyncio  # noqa
import os  # noqa
import importlib  # noqa
import sqlalchemy  # noqa
import uuid  # noqa

import eave.core.internal.database
import eave.core.internal.orm as orm  # noqa
import eave.core.internal.orm.base
from eave.core.internal.config import CORE_API_APP_CONFIG  # noqa
from eave.stdlib.config import SHARED_CONFIG  # noqa
from eave.stdlib.logging import eaveLogger  # noqa

eave.core.internal.orm.base._load_all()  # noqa: SLF001

db_session = eave.core.internal.database.async_session()

print("Ready to go.")

if __name__ != "__main__":
    raise Exception("This module cannot be imported")
