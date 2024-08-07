import logging
import os
import sys

EAVE_LOGGER = logging.getLogger("eave")

_level_env = os.getenv("LOG_LEVEL") or "INFO"
_level_name = logging.getLevelNamesMapping().get(_level_env.upper(), logging.INFO)

EAVE_LOGGER.setLevel(_level_name)

_stream_handler = logging.StreamHandler(sys.stdout)
_stream_handler.setLevel(_level_name)
EAVE_LOGGER.addHandler(_stream_handler)
