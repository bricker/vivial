import logging
from logging import LogRecord
import sys
from typing import Any, Optional, Self, cast
import uuid
from asgiref.typing import HTTPScope
from starlette.types import Scope

import google.cloud.logging
from eave.stdlib.api_util import get_header_value, get_headers
from eave.stdlib.headers import EAVE_ACCOUNT_ID_HEADER, EAVE_ORIGIN_HEADER, EAVE_REQUEST_ID_HEADER, EAVE_TEAM_ID_HEADER

from eave.stdlib.typing import JsonObject

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


class LogContext(JsonObject):
    @classmethod
    def wrap(cls, ctx: Optional["LogContext"] = None, scope: Optional[HTTPScope | Scope] = None) -> "LogContext":
        return ctx if ctx else cls(scope)

    def __init__(self, scope: Optional[HTTPScope | Scope] = None) -> None:
        self.set({"feature_name": None})
        if scope:
            scope = cast(HTTPScope, scope)
            headers = cast(JsonObject, get_headers(scope))
            self.set({"headers": headers})

            self.set({"eave_request_id": get_header_value(scope, EAVE_REQUEST_ID_HEADER) or str(uuid.uuid4())})
            self.set({"eave_team_id": get_header_value(scope, EAVE_TEAM_ID_HEADER)})
            self.set({"eave_account_id": get_header_value(scope, EAVE_ACCOUNT_ID_HEADER)})
            self.set({"eave_origin": get_header_value(scope, EAVE_ORIGIN_HEADER)})
        else:
            self.set({"eave_request_id": str(uuid.uuid4())})
            self.set({"eave_team_id": None})
            self.set({"eave_account_id": None})
            self.set({"eave_origin": None})

    def set(self, attributes: JsonObject) -> Self:
        self.update(attributes)
        return self

    @property
    def public(self) -> JsonObject:
        return JsonObject(
            {
                "eave_request_id": self.eave_request_id,
            }
        )

    @property
    def eave_account_id(self) -> Optional[str]:
        if v := self.get("eave_account_id"):
            return str(v)
        else:
            return None

    @eave_account_id.setter
    def eave_account_id(self, value: Optional[str]) -> None:
        self.set({"eave_account_id": value})

    @property
    def eave_team_id(self) -> Optional[str]:
        if v := self.get("eave_team_id"):
            return str(v)
        else:
            return None

    @eave_team_id.setter
    def eave_team_id(self, value: Optional[str]) -> None:
        self.set({"eave_team_id": value})

    @property
    def eave_origin(self) -> Optional[str]:
        if v := self.get("eave_origin"):
            return str(v)
        else:
            return None

    @eave_origin.setter
    def eave_origin(self, value: str) -> None:
        self.set({"eave_origin": value})

    @property
    def eave_request_id(self) -> str:
        v = self["eave_request_id"]
        return str(v)

    @property
    def feature_name(self) -> str:
        v = self["feature_name"]
        return str(v)

    @feature_name.setter
    def feature_name(self, value: str) -> None:
        self.set({"feature_name": value})


class EaveLogger:
    _raw_logger = logging.getLogger("eave")

    def __init__(self) -> None:
        pass

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


eaveLogger = EaveLogger()
