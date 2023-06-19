import logging
from logging import LogRecord
import sys
from typing import Optional, Self
import uuid

import google.cloud.logging

from eave.stdlib.typing import JsonObject, JsonValue

from .config import shared_config


# https://stackoverflow.com/a/56944256/885036
class CustomFormatter(logging.Formatter):
    dimgrey = "\x1b[2;39m"
    grey = "\x1b[39;1m"
    yellow = "\x1b[33;1m"
    green = "\x1b[32;1m"
    purple = "\x1b[35;1m"
    cyan = "\x1b[36;1m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    formatstr = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)\n"

    FORMATS = {
        logging.DEBUG: purple + formatstr + reset,
        logging.INFO: cyan + formatstr + reset,
        logging.WARNING: yellow + formatstr + reset,
        logging.ERROR: red + formatstr + reset,
        logging.CRITICAL: bold_red + formatstr + reset,
    }

    IGNORE_KEYS = set(
        [
            "asctime",
            "created",
            "exc_info",
            "exc_text",
            "filename",
            "levelname",
            "levelno",
            "message",
            "module",
            "msecs",
            "msg",
            "name",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
        ]
    )

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        string = formatter.format(record)

        extra = {k: v for k, v in record.__dict__.items() if k not in self.IGNORE_KEYS}
        string += f"{self.dimgrey}{extra}{self.reset}"
        return string


class CustomFilter(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        log = super().filter(record)
        return log and record.name == "eave"


rootLogger = logging.getLogger()
level = shared_config.log_level
rootLogger.setLevel(level)

if shared_config.is_development:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(CustomFormatter())
    handler.addFilter(CustomFilter())
    rootLogger.addHandler(handler)

if shared_config.monitoring_enabled:
    # https://cloud.google.com/python/docs/reference/logging/latest/std-lib-integration
    client = google.cloud.logging.Client()
    client.setup_logging(log_level=level)

eaveLogger = logging.getLogger("eave")


# This format is for Google Cloud Logging
# LogContext = dict[Literal["json_fields"], JsonObject]


class LogContext(JsonObject):
    @classmethod
    def wrap(cls, ctx: Optional["LogContext"]) -> "LogContext":
        return ctx if ctx else cls()

    def getset(self, key: str, default: JsonValue) -> JsonValue:
        """
        Gets the value at the given key. If the key doesn't exist, sets it to the default value.
        Returns the value.
        """
        f = self._ensure_initialized()
        if key in f:
            return f[key]
        else:
            self.set({key: default})
            return default

    def set(self, attributes: JsonObject) -> Self:
        f = self._ensure_initialized()
        f.update(attributes)
        return self

    def get(self, key: str, default: Optional[JsonValue] = None) -> Optional[JsonValue]:
        f = self._ensure_initialized()
        return f.get(key, default)

    def _ensure_initialized(self) -> JsonObject:
        default = JsonObject()
        self.setdefault("json_fields", default)
        return default

    @property
    def request_id(self) -> str:
        v = self.get(key="request_id")
        if v is None:
            v = str(uuid.uuid4())
            self.request_id = v
        return str(v)

    @request_id.setter
    def request_id(self, value: str) -> None:
        self.set({"request_id": value})
