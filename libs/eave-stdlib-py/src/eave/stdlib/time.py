import os
import time

ONE_YEAR_SECONDS = 60 * 60 * 24 * 365

def set_utc() -> None:
    os.environ["TZ"] = "UTC"
    time.tzset()
