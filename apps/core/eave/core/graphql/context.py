from uuid import UUID
from starlette.requests import Request
from starlette.responses import Response

from eave.core.graphql.types.account import Account


class GraphQLContext:
    request: Request
    response: Response
    authenticated_account_id: UUID | None = None
