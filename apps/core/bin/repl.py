import dotenv

dotenv.load_dotenv()

# Import some common modules
import asyncio  # type:ignore  # noqa
import os  # type:ignore  # noqa
import importlib  # type:ignore  # noqa
import sqlalchemy  # type:ignore  # noqa

import eave.core.internal.database  # noqa
import eave.core.internal.orm  # noqa
import eave.core.internal.orm.base  # noqa
from eave.core.internal import app_config  # type:ignore  # noqa
from eave.stdlib.config import shared_config  # type:ignore  # noqa
from eave.stdlib.logging import eaveLogger  # type:ignore  # noqa
import eave.stdlib.analytics as analytics  # type:ignore  # noqa

eave.core.internal.orm.base._load_all() # type:ignore

db_session = eave.core.internal.database.async_session()

print("Ready to go.")

if __name__ != "__main__":
    raise Exception("This module cannot be imported")
