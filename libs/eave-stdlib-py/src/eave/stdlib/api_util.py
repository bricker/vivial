import http
import re
from typing import Optional

import pydantic
from eave.stdlib.exceptions import MissingRequiredHeaderError
from eave.stdlib.headers import AUTHORIZATION_HEADER, COOKIE_HEADER, EAVE_SIGNATURE_HEADER

import eave.stdlib.util as util
from starlette.responses import Response
from asgiref.typing import HTTPScope

def get_header_value(scope: HTTPScope, name: str) -> str | None:
    """
    This function doesn't support multiple headers with the same name.
    It will always choose the "first" one (from whatever order the ASGI server sent).
    See here for details about the scope["headers"] object:
    https://asgi.readthedocs.io/en/latest/specs/www.html#http-connection-scope
    """
    return next((v.decode() for [n, v] in scope["headers"] if n.decode().lower() == name.lower()), None)

def get_header_value_or_exception(scope: HTTPScope, name: str) -> str:
    """
    Proxy to get_header_value, raises MissingRequiredHeader if header is missing
    """
    v = next((v.decode() for [n, v] in scope["headers"] if n.decode().lower() == name.lower()), None)
    if not v:
        raise MissingRequiredHeaderError(name)
    return v


def get_headers(
    scope: HTTPScope, excluded: Optional[set[str]] = None, redacted: Optional[set[str]] = None
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
            EAVE_SIGNATURE_HEADER,
            AUTHORIZATION_HEADER,
            COOKIE_HEADER,
        ]
    )

    return {
        n.decode(): (v.decode() if n.decode().lower() not in augmented_redacted else util.redact(v.decode()))
        for [n, v] in scope["headers"]
        if n.decode().lower() not in excluded
    }


def get_bearer_token(scope: HTTPScope) -> str | None:
    auth_header = get_header_value(scope=scope, name=AUTHORIZATION_HEADER)
    if auth_header is None:
        return None

    auth_header_match = re.match("^Bearer (.+)$", auth_header)
    if auth_header_match is None:
        return None

    return auth_header_match.group(1)


def json_response(model: pydantic.BaseModel, status_code: int = http.HTTPStatus.OK) -> Response:
    response = Response(status_code=status_code, content=model.json(), media_type="application/json")
    return response
