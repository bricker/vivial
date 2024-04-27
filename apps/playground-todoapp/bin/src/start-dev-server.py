import os
import sys

import uvicorn

from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

sys.path.append(".")

load_standard_dotenv_files()

os.environ["GAE_SERVICE"] = "playground-todoapp"

if __name__ == "__main__":
    uvicorn.run(
        app="eave_playground.todoapp.app:app",
        port=5500,
        reload=True,
        log_level="debug",
        reload_includes=[
            "eave",
        ],
        reload_excludes=[
            "**/build/",
            ".*",
            "**/__pycache__",
            "*.egg-info",
            "**/node_modules",
        ],
    )
