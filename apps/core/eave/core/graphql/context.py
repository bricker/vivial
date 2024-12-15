from typing import NotRequired, TypedDict
from uuid import UUID

from starlette.requests import Request
from starlette.responses import Response


class GraphQLContext(TypedDict):
    request: Request
    response: Response
    authenticated_account_id: NotRequired[UUID]
    visitor_id: NotRequired[str | None]
