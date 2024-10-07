from starlette.requests import Request
from starlette.responses import Response


class GraphQLContext:
    request: Request
    response: Response
