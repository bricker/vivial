# ruff: noqa: E402

import sys

sys.path.append(".")

from eave.dev_tooling.dotenv_loader import load_standard_dotenv_files

load_standard_dotenv_files()

from strawberry.cli import run

if __name__ == "__main__":
    run()
