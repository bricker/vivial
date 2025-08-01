import os
import sys

import uvicorn
import uvicorn.workers

from eave.dev_tooling.constants import EAVE_HOME
from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

sys.path.append(".")

load_standard_dotenv_files()

os.environ["GAE_SERVICE"] = "api"

if __name__ == "__main__":
    uvicorn.run(
        app="eave.core.app:app",
        port=5100,
        reload=True,
        lifespan="on",
        log_level="debug",
        reload_includes=[
            f"{EAVE_HOME}/libs/eave-stdlib-py/src/eave",
        ],
    )
