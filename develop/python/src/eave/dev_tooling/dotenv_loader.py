import os
import dotenv


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


def load_standard_dotenv_files() -> None:
    google_cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT", "eavefyi-dev")
    dotenv.load_dotenv(dotenv_path=os.path.join(os.environ["EAVE_HOME"], "develop/shared/share.env"), override=True)
    dotenv.load_dotenv(dotenv_path=os.path.join(os.environ["EAVE_HOME"], ".env"), override=True)
    dotenv.load_dotenv(dotenv_path=os.path.join(os.environ["EAVE_HOME"], f".{google_cloud_project}.env"), override=True)
