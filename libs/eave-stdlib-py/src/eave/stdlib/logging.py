import logging
import sys

import google.cloud.logging

from .config import shared_config

logger = logging.getLogger("eave")


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
        logging.DEBUG: grey + formatstr + reset,
        logging.INFO: green + formatstr + reset,
        logging.WARNING: yellow + formatstr + reset,
        logging.ERROR: red + formatstr + reset,
        logging.CRITICAL: bold_red + formatstr + reset,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_logging(level: int = logging.INFO) -> None:
    logger.setLevel(level)

    if shared_config.dev_mode:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        formatter = CustomFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if shared_config.monitoring_enabled:
        client = google.cloud.logging.Client()
        client.setup_logging(log_level=level)
