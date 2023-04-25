import time
import os

def set_utc() -> None:
    os.environ["TZ"] = "UTC"
    time.tzset()
