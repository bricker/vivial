import http
import re

import aiohttp
from asgiref.typing import HTTPScope
from starlette.responses import Response
from starlette.types import Scope

from eave.stdlib import util
from eave.stdlib.http_exceptions import BadRequestError


def get_header_value(scope: Scope | HTTPScope, name: str) -> str | None:
    """
    This function doesn't support multiple headers with the same name.
    It will always choose the "first" one (from whatever order the ASGI server sent).
    See here for details about the scope["headers"] object:
    https://asgi.readthedocs.io/en/latest/specs/www.html#http-connection-scope
    """
    return next((v.decode() for [n, v] in scope["headers"] if n.decode().lower() == name.lower()), None)


class MissingRequiredHeaderError(BadRequestError):
    pass


def get_header_value_or_exception(scope: Scope | HTTPScope, name: str) -> str:
    """
    Proxy to get_header_value, raises MissingRequiredHeader if header is missing
    """
    v = next((v.decode() for [n, v] in scope["headers"] if n.decode().lower() == name.lower()), None)
    if not v:
        raise MissingRequiredHeaderError(name)
    return v


def get_headers(
    scope: Scope | HTTPScope, excluded: set[str] | None = None, redacted: set[str] | None = None
) -> dict[str, str | None]:
    """
    This function doesn't support multiple headers with the same name.
    It will always choose the "first" one (from whatever order the ASGI server sent).
    See here for details about the scope["headers"] object:
    https://asgi.readthedocs.io/en/latest/specs/www.html#http-connection-scope
    """
    if excluded is None:
        excluded = set[str]()
    if redacted is None:
        redacted = set[str]()

    augmented_redacted = redacted.union(
        [
            aiohttp.hdrs.AUTHORIZATION.lower(),
            aiohttp.hdrs.COOKIE.lower(),
        ]
    )

    return {
        n.decode(): (v.decode() if n.decode().lower() not in augmented_redacted else util.redact(v.decode()))
        for [n, v] in scope["headers"]
        if n.decode().lower() not in excluded
    }


def get_bearer_token(scope: Scope | HTTPScope) -> str | None:
    auth_header = get_header_value(scope=scope, name=aiohttp.hdrs.AUTHORIZATION)
    if auth_header is None:
        return None

    auth_header_match = re.match("^Bearer (.+)$", auth_header)
    if auth_header_match is None:
        return None

    return auth_header_match.group(1)


def set_redirect(response: Response, location: str) -> Response:
    response.headers[aiohttp.hdrs.LOCATION] = location
    response.status_code = http.HTTPStatus.TEMPORARY_REDIRECT
    return response
