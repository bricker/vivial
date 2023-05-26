import logging
import sys
from typing import Any, Literal, Mapping, Optional, Self, TypeVar, cast

import google.cloud.logging

from eave.stdlib.typing import JsonObject

from .config import shared_config


# https://stackoverflow.com/a/56944256/885036
class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;1m"
    yellow = "\x1b[33;1m"
    green = "\x1b[32;1m"
    purple = "\x1b[35;1m"
    cyan = "\x1b[36;1m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    formatstr = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: purple + formatstr + reset,
        logging.INFO: cyan + formatstr + reset,
        logging.WARNING: yellow + formatstr + reset,
        logging.ERROR: red + formatstr + reset,
        logging.CRITICAL: bold_red + formatstr + reset,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


rootLogger = logging.getLogger()
level = shared_config.log_level
rootLogger.setLevel(level)

if shared_config.is_development:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = CustomFormatter()
    handler.setFormatter(formatter)
    rootLogger.addHandler(handler)

if shared_config.monitoring_enabled:
    # https://cloud.google.com/python/docs/reference/logging/latest/std-lib-integration
    client = google.cloud.logging.Client()
    client.setup_logging(log_level=level)

eaveLogger = logging.getLogger("eave")


# This format is for Google Cloud Logging
# LogContext = dict[Literal["json_fields"], JsonObject]

T = TypeVar("T")
class LogContext(dict[str, object]):
    @classmethod
    def wrap(cls, ctx: Optional["LogContext"]) -> "LogContext":
        return ctx if ctx else cls()

    def getset(self, key: str, default: T) -> T:
        """
        Gets the value at the given key. If the key doesn't exist, sets it to the default value.
        Returns the value.
        """
        f = self.setdefault("json_fields", JsonObject())
        fc = cast(JsonObject, f)
        if key in fc:
            return fc[key]
        else:
            self.set({key: default})
            return default

    def set(self, attributes: JsonObject) -> Self:
        f = self.setdefault("json_fields", dict[str, JsonObject]())
        fc = cast(JsonObject, f)
        fc.update(attributes)
        return self

    def get(self, key: str, default: Optional[Any | T] = None) -> Any | T | None:
        f = self.setdefault("json_fields", dict[str, JsonObject]())
        fc = cast(JsonObject, f)
        return fc.get(key, default)
