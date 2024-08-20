import logging
import sys

from eave.collectors.core.agent import EaveAgent
from eave.collectors.core import config
# from eave.collectors.core.credentials import EaveCredentials

EAVE_LOGGER_NAME = "eave"
EAVE_LOGGER = logging.getLogger(EAVE_LOGGER_NAME)

class _EaveTelemetryHandler(logging.Handler):
    _agent: EaveAgent

    def __init__(self, level: int | str = 0) -> None:
        super().__init__(level)
        self._agent = EaveAgent()
        self._agent.start()

    def emit(self, record: logging.LogRecord) -> None:
        self._agent.put(record)


class _EaveTelemetryFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        log = super().filter(record)
        return log and record.name == EAVE_LOGGER_NAME

if not config.telemetry_disabled():
    _eave_telemetry_filter = _EaveTelemetryFilter()
    _eave_telemetry_handler = _EaveTelemetryHandler()
    _eave_telemetry_handler.addFilter(_eave_telemetry_filter)
    EAVE_LOGGER.addHandler(_eave_telemetry_handler)

if config.is_development():
    EAVE_LOGGER.setLevel(logging.DEBUG)

    _stream_handler = logging.StreamHandler(sys.stdout)
    _stream_handler.setLevel(logging.DEBUG)
    EAVE_LOGGER.addHandler(_stream_handler)
