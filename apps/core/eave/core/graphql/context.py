from typing import NotRequired, TypedDict
from uuid import UUID

from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib.analytics import AnalyticsContext
from eave.stdlib.logging import LOGGER
from eave.stdlib.typing import JsonObject


class GraphQLContext(TypedDict):
    request: Request
    response: Response
    authenticated_account_id: NotRequired[UUID]
    visitor_id: NotRequired[str | None]
    operation_name: NotRequired[str | None]
    operation_type: NotRequired[str | None]
    correlation_id: NotRequired[str]
    client_ip: NotRequired[str | None]
    client_geo: NotRequired[JsonObject]
    extra: NotRequired[JsonObject]


def log_ctx(context: GraphQLContext) -> JsonObject:
    # the `info.context` passed into this function is typed as `Any`, so this try/catch is for runtime safety
    try:
        authenticated_account_id = context.get("authenticated_account_id")
        correlation_id = context.get("correlation_id")
        client_geo = context.get("client_geo")
        client_ip = context.get("client_ip")
        http_request = context.get("request")
        http_response = context.get("response")
        extra = context.get("extra")
        rest = {**extra} if extra else {}

        return {
            "source": "graphql",
            "authenticated_account_id": str(authenticated_account_id) if authenticated_account_id else None,
            "visitor_id": context.get("visitor_id"),
            "operation_name": context.get("operation_name"),
            "operation_type": context.get("operation_type"),
            "correlation_id": correlation_id,
            "client_geo": client_geo,
            "client_ip": client_ip,
            "http_request": {
                # https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#HttpRequest
                "requestMethod": http_request.method,
                "requestUrl": str(http_request.url),
                # "requestSize": 0,
                "status": http_response.status_code,
                # "responseSize": 0,
                "userAgent": http_request.headers.get("user-agent"),
                "remoteIp": client_ip,
                # "serverIp": string,
                "referer": http_request.headers.get("referer"),
                # "latency": string,
                # "cacheLookup": boolean,
                # "cacheHit": boolean,
                # "cacheValidatedWithOriginServer": boolean,
                # "cacheFillBytes": string,
                "protocol": http_request.url.scheme,
            },
            **rest,
        }
    except Exception as e:
        LOGGER.exception(e)
        return {
            "source": "graphql",
        }


def analytics_ctx(context: GraphQLContext) -> AnalyticsContext:
    authenticated_account_id = context.get("authenticated_account_id")

    return AnalyticsContext(
        {
            "authenticated_account_id": str(authenticated_account_id) if authenticated_account_id else None,
            "visitor_id": context.get("visitor_id"),
            "correlation_id": context.get("correlation_id"),
            "client_geo": context.get("client_geo"),
            "client_ip": context.get("client_ip"),
        }
    )
