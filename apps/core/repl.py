import dotenv

dotenv.load_dotenv()

# Import some common modules
import asyncio # noqa
import time
from datetime import datetime
import eave.core.internal.orm.base # noqa
import eave.core.internal.orm # noqa
import eave.core.internal.database # noqa
from eave.core.internal import app_config # noqa
import eave.stdlib # noqa
import eave.stdlib.core_api # noqa

eave.core.internal.orm.base._load_all()

print("Ready to go.")

if __name__ != "__main__":
    raise Exception("This module cannot be imported")
