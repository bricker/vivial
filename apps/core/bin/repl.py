import dotenv

dotenv.load_dotenv()

# Import some common modules
import asyncio  # noqa
import os  # noqa
import importlib  # noqa
import sqlalchemy  # noqa

import eave.core.internal.database  # noqa
import eave.core.internal.orm  # noqa
import eave.core.internal.orm.base  # noqa
from eave.core.internal import app_config  # noqa
from eave.stdlib.config import shared_config  # noqa
from eave.stdlib.logging import eaveLogger  # noqa
import eave.stdlib.analytics as analytics  # noqa

eave.core.internal.orm.base._load_all()

db_session = eave.core.internal.database.async_session()  # noqa

print("Ready to go.")

if __name__ != "__main__":
    raise Exception("This module cannot be imported")
