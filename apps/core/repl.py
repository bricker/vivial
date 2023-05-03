import dotenv

dotenv.load_dotenv()

import asyncio
from typing import Any, Coroutine

# Import some common modules
import eave.core.internal.orm.base
import eave.core.internal.orm


def run_coro(func: Coroutine[Any, Any, Any]) -> None:
    asyncio.run(func)


eave.core.internal.orm.base._load_all()

print("Ready to go.")

if __name__ != "__main__":
    raise Exception("This module cannot be imported")
