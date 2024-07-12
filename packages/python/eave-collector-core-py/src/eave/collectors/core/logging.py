import logging
import os
import sys

EAVE_LOGGER = logging.getLogger("eave")

if os.getenv("EAVE_ENV") == "development":
    EAVE_LOGGER.setLevel(logging.DEBUG)

    _stream_handler = logging.StreamHandler(sys.stdout)
    _stream_handler.setLevel(logging.DEBUG)
    EAVE_LOGGER.addHandler(_stream_handler)
