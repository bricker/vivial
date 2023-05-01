import dotenv

dotenv.load_dotenv()

import asyncio
from typing import Any, Coroutine

# Import some common modules
import eave.core.internal.orm as eave_orm
from eave.core.internal.config import app_config as app_config

def run_coro(func: Coroutine[Any, Any, Any]) -> None:
    asyncio.run(func)


eave_orm._load_all()

print("Ready to go.")

if __name__ != "__main__":
    raise Exception("This module cannot be imported")
