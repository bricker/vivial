from typing import NotRequired, TypedDict
from uuid import UUID

from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib.logging import LOGGER
from eave.stdlib.typing import JsonObject

class GraphQLContext(TypedDict):
    request: Request
    response: Response
    authenticated_account_id: NotRequired[UUID]
    visitor_id: NotRequired[str | None]
    operation_name: NotRequired[str | None]
    operation_type: NotRequired[str | None]
    request_id: NotRequired[str]
    extra: NotRequired[JsonObject]

def log_ctx(context: GraphQLContext) -> JsonObject:
    # the `info.context` passed into this function is typed as `Any`, so this try/catch is for runtime safety
    try:
        authenticated_account_id = context.get("authenticated_account_id")
        request_id = context.get("request_id")
        extra = context.get("extra")
        rest = { **extra } if extra else {}

        return {
            "source": "graphql",
            "authenticated_account_id": str(authenticated_account_id) if authenticated_account_id else None,
            "visitor_id": context.get("visitor_id"),
            "operation_name": context.get("operation_name"),
            "operation_type": context.get("operation_type"),
            "request_id": str(request_id) if request_id else None,
            **rest,
        }
    except Exception as e:
        LOGGER.exception(e)
        return {
            "source": "graphql",
        }
