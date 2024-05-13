import logging
import sys
import uuid
from logging import Logger, LogRecord
from typing import Any, Optional, Self, TypedDict, cast

from eave.stdlib.util import erasetype
import google.cloud.logging
from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.types import Scope

from eave.stdlib.api_util import get_header_value, get_headers
from eave.stdlib.typing import JsonObject, JsonValue

from .config import SHARED_CONFIG
from .utm_cookies import get_tracking_cookies


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

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.get_formatstr(record.levelno, self.formatstr)
        formatter = logging.Formatter(log_fmt)
        string = formatter.format(record)

        extra = {k: v for k, v in record.__dict__.items() if k not in CustomFormatter.IGNORE_KEYS}
        string += f"{self.dimgrey}{extra}{self.reset}"
        return string


class CustomFilter(logging.Filter):
    _whitelist_records = ("eave",)

    def filter(self, record: LogRecord) -> bool:
        log = super().filter(record)
        return log and record.name in self._whitelist_records


_SCOPE_KEY = "eave_state"

class LogContext(JsonObject):
    @classmethod
    def load(
        cls, scope: HTTPScope | Scope
    ) -> "LogContext":
        if "extensions" not in scope or scope["extensions"] is None:
            scope["extensions"] = {}

        if ctx := scope["extensions"].get(_SCOPE_KEY):
            return cast(LogContext, ctx)
        else:
            ctx = LogContext()
            scope["extensions"][_SCOPE_KEY] = cast(Any, ctx)
            return ctx

    def __init__(self) -> None:
        self.eave_request_id = uuid.uuid4().hex

    @property
    def public(self) -> JsonObject:
        return JsonObject(
            {
                "eave_request_id": self.eave_request_id,
            }
        )

    @property
    def eave_visitor_id(self) -> str | None:
        return str(v) if (v := self.get("eave_visitor_id")) else None

    @eave_visitor_id.setter
    def eave_visitor_id(self, value: str | None) -> None:
        self["eave_visitor_id"] = value

    @property
    def eave_authed_account_id(self) -> str | None:
        return str(v) if (v := self.get("eave_authed_account_id")) else None

    @eave_authed_account_id.setter
    def eave_authed_account_id(self, value: str | None) -> None:
        self["eave_authed_account_id"] = value

    @property
    def eave_authed_team_id(self) -> str | None:
        return str(v) if (v := self.get("eave_authed_team_id")) else None

    @eave_authed_team_id.setter
    def eave_authed_team_id(self, value: str | None) -> None:
        self["eave_authed_team_id"] = value

    @property
    def eave_origin(self) -> str | None:
        return str(v) if (v := self.get("eave_origin")) else None

    @eave_origin.setter
    def eave_origin(self, value: str) -> None:
        self["eave_origin"] = value

    @property
    def eave_request_id(self) -> str:
        return str(self["eave_request_id"])

    @eave_request_id.setter
    def eave_request_id(self, value: str) -> None:
        self["eave_request_id"] = value

    @property
    def feature_name(self) -> str | None:
        return str(v) if (v := self.get("feature_name")) else None

    @feature_name.setter
    def feature_name(self, value: str | None) -> None:
        self["feature_name"] = value


_root_logger = logging.getLogger()
_root_logger.setLevel(SHARED_CONFIG.log_level)

if SHARED_CONFIG.is_development or SHARED_CONFIG.is_test:
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

    def debug(self, msg: str | Exception, *args: JsonObject | LogContext | None, **kwargs: Any) -> None:
        self._raw_logger.debug(**self._preparekwargs(msg, *args, **kwargs))

    def info(self, msg: str | Exception, *args: JsonObject | LogContext | None, **kwargs: Any) -> None:
        self._raw_logger.info(**self._preparekwargs(msg, *args, **kwargs))

    def warning(self, msg: str | Exception, *args: JsonObject | LogContext | None, **kwargs: Any) -> None:
        self._raw_logger.warning(**self._preparekwargs(msg, *args, **kwargs))

    def error(self, msg: str | Exception, *args: JsonObject | LogContext | None, **kwargs: Any) -> None:
        kwargs.setdefault("exc_info", True)
        self._raw_logger.error(**self._preparekwargs(msg, *args, **kwargs))

    def exception(self, msg: str | Exception, *args: JsonObject | LogContext | None, **kwargs: Any) -> None:
        kwargs.setdefault("exc_info", True)
        self._raw_logger.exception(**self._preparekwargs(msg, *args, **kwargs))

    def critical(self, msg: str | Exception, *args: JsonObject | LogContext | None, **kwargs: Any) -> None:
        kwargs.setdefault("exc_info", True)
        self._raw_logger.critical(**self._preparekwargs(msg, *args, **kwargs))

    def _preparekwargs(
        self, msg: str | Exception, *args: JsonObject | LogContext | None, **kwargs: Any
    ) -> dict[str, Any]:
        if isinstance(msg, Exception):
            kwargs["exc_info"] = msg

        kwargs.setdefault("stacklevel", 2)
        extra = kwargs.pop("extra", {})

        return {
            "msg": str(msg),
            "extra": JsonObject(
                {
                    "json_fields": {
                        "metadata": {
                            "eave": {
                                **extra,
                                **{k: v for a in args if a for k, v in a.items()},
                            },
                        },
                    },
                },
            ),
            **kwargs,
        }


# Should be eave_logger to conform to pep8, but this is already used heavily throughout this project.
eaveLogger = EaveLogger()  # noqa: N816
LOGGER = eaveLogger  # This alias makes auto-importing easier
