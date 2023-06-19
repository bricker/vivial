import logging
from logging import LogRecord
import sys
from typing import Any, Literal, Optional, Self, cast
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

# This format is for Google Cloud Logging

class LogContext(JsonObject):
    @classmethod
    def wrap(cls, ctx: Optional["LogContext"]) -> "LogContext":
        return ctx if ctx else cls()

    def set(self, attributes: JsonObject) -> Self:
        self.update(attributes)
        return self

    @property
    def request_id(self) -> str:
        v = self.get("request_id")
        if v is None:
            v = str(uuid.uuid4())
            self.request_id = v
        return str(v)

    @request_id.setter
    def request_id(self, value: str) -> None:
        self.set({"request_id": value})

class EaveLogger:
    _raw_logger = logging.getLogger("eave")

    def __init__(self) -> None:
        pass

    def debug(self, msg: str | Exception, *args: JsonObject | LogContext | None, **kwargs: Any) -> None:
        self._raw_logger.debug(
            msg=str(msg),
            extra=self._makeextra(*args),
            **self._preparekwargs(msg, kwargs),
        )

    def info(self, msg: str | Exception, *args: JsonObject | LogContext | None, **kwargs: Any) -> None:
        self._raw_logger.info(
            msg=str(msg),
            extra=self._makeextra(*args),
            **self._preparekwargs(msg, kwargs),
        )

    def warning(self, msg: str | Exception, *args: JsonObject | LogContext | None, **kwargs: Any) -> None:
        self._raw_logger.warning(
            str(msg),
            exc_info=kwargs.pop("exc_info", True),
            extra=self._makeextra(*args),
            **self._preparekwargs(msg, kwargs),
        )

    def error(self, msg: str | Exception, *args: JsonObject | LogContext | None, **kwargs: Any) -> None:
        self._raw_logger.error(
            msg=str(msg),
            exc_info=kwargs.pop("exc_info", True),
            extra=self._makeextra(*args),
            **self._preparekwargs(msg, kwargs),
        )

    def exception(self, msg: str | Exception, *args: JsonObject | LogContext | None, **kwargs: Any) -> None:
        self._raw_logger.exception(
            msg=str(msg),
            exc_info=kwargs.pop("exc_info", True),
            extra=self._makeextra(*args),
            **self._preparekwargs(msg, kwargs),
        )

    def critical(self, msg: str | Exception, *args: JsonObject | LogContext | None, **kwargs: Any) -> None:
        self._raw_logger.critical(
            msg=str(msg),
            exc_info=kwargs.pop("exc_info", True),
            extra=self._makeextra(*args),
            **self._preparekwargs(msg, kwargs),
        )

    def _makeextra(self, *args: JsonObject | LogContext | None) -> JsonObject | None:
        return JsonObject({
            "json_fields": {
                "metadata": {
                    "eave": {
                        **{k:v for a in args if a for k,v in a}
                    },
                },
            },
        })

    def _preparekwargs(self, msg: str | Exception, kwargs: dict[str, Any]) -> dict[str, Any]:
        if isinstance(msg, Exception):
            kwargs.setdefault("exc_info", msg)

        kwargs.setdefault("stacklevel", 2)
        return kwargs

eaveLogger = EaveLogger()
