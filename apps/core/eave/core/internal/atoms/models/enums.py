from enum import StrEnum
from typing import Self
from eave.stdlib.logging import LOGGER


class HttpRequestMethod(StrEnum):
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    GET = "GET"

    @classmethod
    def from_str(cls, s: str) -> Self | None:
        try:
            return cls.__call__(value=s.upper())
        except ValueError as e:
            LOGGER.warning(e)
            return None

class BrowserAction(StrEnum):
    CLICK = "CLICK"
    FORM_SUBMISSION = "FORM_SUBMISSION"
    PAGE_VIEW = "PAGE_VIEW"

    @classmethod
    def from_str(cls, s: str) -> Self | None:
        try:
            return cls.__call__(value=s.upper())
        except ValueError:
            return None
