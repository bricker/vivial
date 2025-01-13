from typing import NotRequired, TypedDict, cast
from uuid import UUID

from asgiref.typing import HTTPScope
from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib.analytics import AnalyticsContext
from eave.stdlib.logging import LOGGER
from eave.stdlib.typing import JsonObject


class ClientGeo(TypedDict):
    region: str | None
    subdivision: str | None
    city: str | None
    coordinates: str | None


class LogContextHttpRequest(TypedDict, total=False):
    """
    This mimics http_request_pb2.HttpRequest, but in a way that the static analyzer can use.
    https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#httprequest
    """

    requestMethod: str
    requestUrl: str
    requestSize: str
    status: int
    responseSize: str
    userAgent: str
    remoteIp: str
    serverIp: str
    referer: str
    latency: str
    cacheLookup: bool
    cacheHit: bool
    cacheValidatedWithOriginServer: bool
    cacheFillBytes: str
    protocol: str


class LogContext(TypedDict, total=False):
    http_request: LogContextHttpRequest
    authenticated_account_id: str | None
    visitor_id: str | None
    correlation_id: str | None
    operation_name: str | None
    operation_type: str | None
    operation_start: str | None
    client_geo: ClientGeo | None
    client_ip: str | None
    extra: dict[str, object]


class GraphQLContext(TypedDict):
    request: Request
    response: Response
    authenticated_account_id: NotRequired[UUID]
    visitor_id: NotRequired[str | None]
    operation_name: NotRequired[str | None]
    operation_type: NotRequired[str | None]
    operation_start_datetime_iso: NotRequired[str]
    operation_duration: NotRequired[float]
    correlation_id: NotRequired[str]
    client_ip: NotRequired[str | None]
    client_geo: NotRequired[ClientGeo]
    extra: NotRequired[dict[str, object]]


def log_ctx(context: GraphQLContext) -> LogContext:
    result: LogContext = {}

    try:
        # the `context` passed into this function is typed as `Any`, so this try/catch is for runtime safety
        # Also, we're inserting attributes one-by-one so that in case of an error, the exception log has at least partial information.
        request = context.get("request")
        response = context.get("response")
        scope = cast(HTTPScope, request.scope)

        # https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#HttpRequest
        # Note that for LogEntry.HttpRequest we explicitly omit keys instead of setting them to "None", because "None" values aren't parsed out in Cloud Logging.
        log_http_request: LogContextHttpRequest = {}
        result["http_request"] = log_http_request
        result["http_request"]["requestMethod"] = request.method
        result["http_request"]["requestUrl"] = str(request.url)

        authenticated_account_id = context.get("authenticated_account_id")
        result["authenticated_account_id"] = str(authenticated_account_id) if authenticated_account_id else None
        result["visitor_id"] = context.get("visitor_id")
        result["correlation_id"] = context.get("correlation_id")
        result["operation_name"] = context.get("operation_name")
        result["operation_type"] = context.get("operation_type")
        result["operation_start"] = context.get("operation_start_datetime_iso")
        result["client_geo"] = context.get("client_geo")

        if operation_duration := context.get("operation_duration"):
            # https://protobuf.dev/reference/protobuf/google.protobuf/#duration
            result["http_request"]["latency"] = f"{operation_duration}s"

        if user_agent := request.headers.get("user-agent"):
            result["http_request"]["userAgent"] = user_agent

        if referer := request.headers.get("referer"):
            result["http_request"]["referer"] = referer

        if status_code := response.status_code:
            # response.status_code is a (non-optional) int, but Strawberry initially sets it to `None` until the operation has finished executing.
            # If we check `is None` here, the static analyzer gives a warning because it thinks that case is impossible,
            # so we do a "falsey" check, which for any valid status code will be True.
            result["http_request"]["status"] = status_code

        client_ip = context.get("client_ip")
        if not client_ip and scope["client"]:
            try:
                # Since we're riskily deconstructing a tuple from an external system, try/except in case of unexpected tuple structure at runtime.
                client_ip, _ = scope["client"]
            except Exception as e:
                LOGGER.exception(e, result)

        result["client_ip"] = client_ip
        if client_ip:
            result["http_request"]["remoteIp"] = client_ip

        if scope["server"]:
            try:
                ip, port = scope["server"]
                server_ip = f"{ip}"
                if port:
                    server_ip += f":{port}"
                result["http_request"]["serverIp"] = server_ip
            except Exception as e:
                # Since we're riskily deconstructing a tuple from an external system, try/except in case of unexpected tuple structure at runtime.
                LOGGER.exception(e, result)

        if extra := context.get("extra"):
            result["extra"] = extra

    except Exception as e:
        LOGGER.exception(e, result)

    return result


def analytics_ctx(context: GraphQLContext) -> AnalyticsContext | None:
    try:
        # the `context` passed into this function is typed as `Any`, so this try/catch is for runtime safety
        authenticated_account_id = context.get("authenticated_account_id")

        return AnalyticsContext(
            {
                "authenticated_account_id": str(authenticated_account_id) if authenticated_account_id else None,
                "visitor_id": context.get("visitor_id"),
                "correlation_id": context.get("correlation_id"),
                "client_geo": cast(JsonObject, context.get("client_geo")),
                "client_ip": context.get("client_ip"),
            }
        )
    except Exception as e:
        LOGGER.exception(e, log_ctx(context))

    return None
