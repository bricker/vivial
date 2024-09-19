import logging
import sys

from eave.collectors.core import config
from eave.collectors.core.agent import EaveAgent
from eave.collectors.core.agent.data_handler.logs import LogsHandler
from eave.collectors.core.datastructures import LogPayload

_EAVE_LOGGER_NAME = "eave-collector-telemetry"
_EAVE_ROOT_LOGGER = logging.getLogger(_EAVE_LOGGER_NAME)
_EAVE_LOGGING_AGENT_LOGGER = logging.getLogger("eave-logging")


class _EaveTelemetryHandler(logging.Handler):
    _agent: EaveAgent

    def __init__(self, level: int | str = 0) -> None:
        super().__init__(level)
        # intentionally give telem agent a separate logger from the one
        # used by the atom agent, so as to not cause inf loop of logger
        # generating logs it then feeds to its own write queue
        self._agent = EaveAgent(logger=_EAVE_LOGGING_AGENT_LOGGER, data_handler=LogsHandler())
        self._agent.start()

    def emit(self, record: logging.LogRecord) -> None:
        self._agent.put(LogPayload.from_record(record))


class _EaveTelemetryFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        log = super().filter(record)
        return log and record.name.startswith(_EAVE_LOGGER_NAME)


if not config.telemetry_disabled():
    _eave_telemetry_filter = _EaveTelemetryFilter()
    _eave_telemetry_handler = _EaveTelemetryHandler()
    _eave_telemetry_handler.addFilter(_eave_telemetry_filter)
    _EAVE_ROOT_LOGGER.addHandler(_eave_telemetry_handler)

if config.is_development():
    _EAVE_ROOT_LOGGER.setLevel(logging.DEBUG)

    _stream_handler = logging.StreamHandler(sys.stdout)
    _stream_handler.setLevel(logging.DEBUG)
    _EAVE_ROOT_LOGGER.addHandler(_stream_handler)
    _EAVE_LOGGING_AGENT_LOGGER.addHandler(_stream_handler)


def eave_logger_factory(pkg_name: str) -> logging.Logger:
    """
    Build a logger for use in an Eave atom collector
    """
    # create a child collector of _EAVE_LOGGER to include collector
    # package name in the logger name
    log_name = pkg_name if pkg_name.startswith(_EAVE_LOGGER_NAME) else f"{_EAVE_LOGGER_NAME}.{pkg_name}"
    logger = logging.getLogger(log_name)

    # propogate logs to parent logger _EAVE_LOGGER
    # which will do the real work of sending the log to eave backend
    logger.propagate = True
    return logger


EAVE_CORE_LOGGER = eave_logger_factory("eave-collector-core-py")
