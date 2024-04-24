import os

import dotenv

from eave.dev_tooling.constants import EAVE_HOME


def merged_dotenv_values(files: list[str]) -> dict[str, str]:
    env = os.environ.copy()
    for f in files:
        values = dotenv.dotenv_values(f)
        valuesnormalized = {k: v for k, v in values.items() if v is not None}
        env.update(valuesnormalized)

    return env


def load_merged_dotenv_files(files: list[str]) -> None:
    for f in files:
        dotenv.load_dotenv(f, override=False)


def load_dotenv(path: str, *, override: bool = True) -> None:
    dotenv.load_dotenv(dotenv_path=os.path.join(EAVE_HOME, path), override=override)


def load_standard_dotenv_files() -> None:
    eave_env = os.getenv("EAVE_ENV", "development")
    load_dotenv(f".{eave_env}.env", override=False)
    load_dotenv(".env", override=False)
    load_dotenv(f"develop/shared/share.{eave_env}.env", override=False)
    load_dotenv("develop/shared/share.env", override=False)
