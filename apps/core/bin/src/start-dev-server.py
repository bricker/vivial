import os
import sys

import uvicorn

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
        log_level="debug",
        reload_includes=[
            "eave",
            f"{EAVE_HOME}/libs/eave-stdlib-py/src/eave",
        ],
        reload_excludes=[
            "**/build/",
            ".*",
            "**/__pycache__",
            "*.egg-info",
            "**/node_modules",
        ],
    )
