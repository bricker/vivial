import dotenv
dotenv.load_dotenv()

import asyncio
from typing import Any, Coroutine
import eave.core.app

# Import some common modules
import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
from eave.core.internal.config import app_config
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.operations as eave_ops
import eave.stdlib.core_api.enums as eave_enums
import eave.stdlib.core_api.client as eave_core


def run_coro(func: Coroutine[Any, Any, Any]) -> None:
    asyncio.run(func)

eave_orm._load_all()

print("Ready to go.")

if __name__ != "__main__":
    raise Exception("This module cannot be imported")
