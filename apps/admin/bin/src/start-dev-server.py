import os
import sys

import uvicorn

from eave.dev_tooling.constants import EAVE_HOME
from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

sys.path.append(".")

load_standard_dotenv_files()

os.environ["GAE_SERVICE"] = "admin"

if __name__ == "__main__":
    uvicorn.run(
        app="eave.admin.app:app",
        port=5200,
        reload=True,
        log_level="debug",
        reload_includes=[
            f"{EAVE_HOME}/libs/eave-stdlib-py/src/eave",
        ],
    )
