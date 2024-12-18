from typing import NotRequired, TypedDict
from uuid import UUID

from starlette.requests import Request
from starlette.responses import Response


class AdminGraphQLContext(TypedDict):
    request: Request
    response: Response
