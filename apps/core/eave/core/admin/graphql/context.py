from typing import TypedDict

from starlette.requests import Request
from starlette.responses import Response


class AdminGraphQLContext(TypedDict):
    request: Request
    response: Response
