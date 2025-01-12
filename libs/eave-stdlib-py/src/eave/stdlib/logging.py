import dataclasses
import logging
import sys
from logging import Logger, LogRecord
from typing import Any, override

import google.cloud.logging

from eave.stdlib.typing import JsonObject, JsonValue

from .config import SHARED_CONFIG


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

    @classmethod
    def get_formatstr(cls, levelno: int, message: str) -> str:
        match levelno:
            case logging.DEBUG:
                return cls.purple + message + cls.reset
            case logging.INFO:
                return cls.cyan + message + cls.reset
            case logging.WARNING:
                return cls.yellow + message + cls.reset
            case logging.ERROR:
                return cls.red + message + cls.reset
            case logging.CRITICAL:
                return cls.bold_red + message + cls.reset
            case _:
                return message

    IGNORE_KEYS = (
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
    )

    @override
    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.get_formatstr(record.levelno, self.formatstr)
        formatter = logging.Formatter(log_fmt)
        string = formatter.format(record)

        extra = {k: v for k, v in record.__dict__.items() if k not in CustomFormatter.IGNORE_KEYS}
        string += f"{self.dimgrey}{extra}{self.reset}"
        return string


class CustomFilter(logging.Filter):
    _whitelist_records = ("eave", "strawberry.execution")

    @override
    def filter(self, record: LogRecord) -> bool:
        log = super().filter(record)
        if SHARED_CONFIG.log_level == logging.DEBUG:
            return True
        else:
            return log and record.name in self._whitelist_records


_root_logger = logging.getLogger()
_root_logger.setLevel(SHARED_CONFIG.log_level)

if SHARED_CONFIG.is_local:
    _stream_handler = logging.StreamHandler(sys.stdout)
    _stream_handler.setLevel(SHARED_CONFIG.log_level)
    _stream_handler.setFormatter(CustomFormatter())
    _stream_handler.addFilter(CustomFilter())
    _root_logger.addHandler(_stream_handler)

if SHARED_CONFIG.monitoring_enabled:
    # https://cloud.google.com/python/docs/reference/logging/latest/std-lib-integration
    _gcp_log_client = google.cloud.logging.Client()
    _gcp_log_client.setup_logging(log_level=SHARED_CONFIG.log_level)


class EaveLogger:
    _raw_logger: Logger

    def __init__(self) -> None:
        self._raw_logger = logging.getLogger("eave")
        self._raw_logger.setLevel(SHARED_CONFIG.log_level)

    def f(self, level: int, message: str) -> str:
        return CustomFormatter.get_formatstr(level, message)

    def fprint(self, level: int, message: str) -> None:
        print(self.f(level, message))

    def debug(self, msg: str | Exception, *args: JsonObject | None, **kwargs: Any) -> None:
        self._raw_logger.debug(**self._preparekwargs(msg, *args, **kwargs))

    def info(self, msg: str | Exception, *args: JsonObject | None, **kwargs: Any) -> None:
        self._raw_logger.info(**self._preparekwargs(msg, *args, **kwargs))

    def warning(self, msg: str | Exception, *args: JsonObject | None, **kwargs: Any) -> None:
        self._raw_logger.warning(**self._preparekwargs(msg, *args, **kwargs))

    def error(self, msg: str | Exception, *args: JsonObject | None, **kwargs: Any) -> None:
        kwargs.setdefault("exc_info", True)
        self._raw_logger.error(**self._preparekwargs(msg, *args, **kwargs))

    def exception(self, msg: str | Exception, *args: JsonObject | None, **kwargs: Any) -> None:
        kwargs.setdefault("exc_info", True)
        self._raw_logger.exception(**self._preparekwargs(msg, *args, **kwargs))

    def critical(self, msg: str | Exception, *args: JsonObject | None, **kwargs: Any) -> None:
        kwargs.setdefault("exc_info", True)
        self._raw_logger.critical(**self._preparekwargs(msg, *args, **kwargs))

    def _preparekwargs(self, msg: str | Exception, *args: JsonObject | None, **kwargs: Any) -> dict[str, Any]:
        if isinstance(msg, Exception):
            kwargs["exc_info"] = True

        kwargs.setdefault("stacklevel", 2)
        extra = kwargs.pop("extra", {})

        eave_extras: JsonObject = {}

        for a in args:
            if a:
                for k, v in a.items():
                    eave_extras[k] = _build_extra(v)

        # This is a special field in Cloud Logging, which sits outside of `json_fields`.
        http_request = eave_extras.pop("http_request")

        return {
            "msg": msg,
            "extra": {
                "http_request": http_request,
                "eave": eave_extras,
                **extra,
            },
            **kwargs,
        }


def _build_extra(v: Any) -> JsonValue:
    if isinstance(v, (int, float, bool)) or v is None:
        return v
    elif isinstance(v, list):
        return [_build_extra(e) for e in v]
    elif isinstance(v, dict):
        return {k: _build_extra(e) for k, e in v.items()}
    elif dataclasses.is_dataclass(v) and not isinstance(v, type):
        return _build_extra(dataclasses.asdict(v))
    else:
        return str(v)


LOGGER = EaveLogger()
