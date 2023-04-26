import os
import time


def set_utc() -> None:
    os.environ["TZ"] = "UTC"
    time.tzset()
