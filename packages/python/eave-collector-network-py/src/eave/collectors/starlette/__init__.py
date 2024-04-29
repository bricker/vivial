# adapted from https://github.com/open-telemetry/opentelemetry-python-contrib/blob/main/instrumentation/opentelemetry-instrumentation-starlette/src/opentelemetry/instrumentation/starlette/__init__.py

# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import typing
import urllib.parse
from functools import wraps
from timeit import default_timer

from asgiref.compatibility import guarantee_single_callable
from starlette import applications
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match

from eave.collectors.core.base_collector import BaseCollector
from eave.collectors.core.correlation_context import corr_ctx
from eave.collectors.core.datastructures import NetworkInEventPayload, NetworkOutEventPayload


# class ASGIGetter:
#     def get(self, carrier: dict, key: str) -> list[str] | None:
#         """Getter implementation to retrieve a HTTP header value from the ASGI
#         scope.

#         Args:
#             carrier: ASGI scope object
#             key: header name in scope
#         Returns:
#             A list with a single string with the header value if it exists,
#                 else None.
#         """
#         headers = carrier.get("headers")
#         if not headers:
#             return None

#         # ASGI header keys are in lower case
#         key = key.lower()
#         decoded = [_value.decode("utf8") for _key, _value in headers if _key.decode("utf8").lower() == key]
#         if not decoded:
#             return None
#         return decoded

#     def keys(self, carrier: dict) -> list[str]:
#         headers = carrier.get("headers") or []
#         return [_key.decode("utf8") for _key, _ in headers]


# asgi_getter = ASGIGetter()


# class ASGISetter:
#     def set(self, carrier: dict, key: str, value: str) -> None:
#         """Sets response header values on an ASGI scope according to `the spec <https://asgi.readthedocs.io/en/latest/specs/www.html#response-start-send-event>`_.

#         Args:
#             carrier: ASGI scope object
#             key: response header name to set
#             value: response header value
#         Returns:
#             None
#         """
#         headers = carrier.get("headers")
#         if not headers:
#             headers = []
#             carrier["headers"] = headers

#         headers.append([key.lower().encode(), value.encode()])


# asgi_setter = ASGISetter()


def get_host_port_url_tuple(scope):
    """Returns (host, port, full_url) tuple."""
    server = scope.get("server") or ["0.0.0.0", 80]
    port = server[1]
    server_host = server[0] + (":" + str(port) if str(port) != "80" else "")
    full_path = scope.get("root_path", "") + scope.get("path", "")
    http_url = scope.get("scheme", "http") + "://" + server_host + full_path
    return server_host, port, http_url


def get_default_span_details(scope: dict) -> tuple[str, dict]:
    """
    Default span name is the HTTP method and URL path, or just the method.
    https://github.com/open-telemetry/opentelemetry-specification/pull/3165
    https://opentelemetry.io/docs/reference/specification/trace/semantic_conventions/http/#name

    Args:
        scope: the ASGI scope dictionary
    Returns:
        a tuple of the span name, and any attributes to attach to the span.
    """
    path = scope.get("path", "").strip()
    method = scope.get("method", "").strip()
    if method and path:  # http
        return f"{method} {path}", {}
    if path:  # websocket
        return path, {}
    return method, {}  # http with no path


# def _censored_url(scope: dict[str, typing.Any]) -> str | None:
#     """
#     Returns the target path as defined by the Semantic Conventions.

#     This value is suitable to use in metrics as it should replace concrete
#     values with a parameterized name. Example: /api/users/{user_id}

#     Refer to the specification
#     https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/metrics/semantic_conventions/http-metrics.md#parameterized-attributes

#     Note: this function requires specific code for each framework, as there's no
#     standard attribute to use.
#     """
#     # FastAPI
#     root_path = scope.get("root_path", "")

#     route = scope.get("route")
#     path_format = getattr(route, "path_format", None)
#     if path_format:
#         return f"{root_path}{path_format}"

#     return None

def remove_url_credentials(url: str) -> str:
    """Given a string url, remove the username and password only if it is a valid url"""

    try:
        parsed = urllib.parse.urlparse(url)
        if all([parsed.scheme, parsed.netloc]):  # checks for valid url
            parsed_url = urllib.parse.urlparse(url)
            netloc = (
                (":".join(((parsed_url.hostname or ""), str(parsed_url.port))))
                if parsed_url.port
                else (parsed_url.hostname or "")
            )
            return urllib.parse.urlunparse(
                (
                    parsed_url.scheme,
                    netloc,
                    parsed_url.path,
                    parsed_url.params,
                    parsed_url.query,
                    parsed_url.fragment,
                )
            )
    except ValueError:  # an unparsable url was passed
        pass
    return url


class EaveASGIMiddleware:
    """The ASGI application middleware.

    This class is an ASGI middleware that starts and annotates spans for any
    requests it is invoked with.

    Args:
        app: The ASGI application callable to forward requests to.
        write_queue: Async batch process queue for dispatching events
    """

    def __init__(
        self,
        app,
        write_queue,
    ):
        self.app = guarantee_single_callable(app)
        self.content_length_header = None
        self.write_queue = write_queue

    async def __call__(self, scope, receive, send):
        """The ASGI application

        Args:
            scope: An ASGI environment.
            receive: An awaitable callable yielding dictionaries
            send: An awaitable callable taking a single dictionary as argument.
        """
        # start = default_timer()
        if scope["type"] not in ("http", "websocket"):
            return await self.app(scope, receive, send)

        _, _, url = get_host_port_url_tuple(scope)
        # TODO: offer config options for URL patterns to exclude?
        # if self.excluded_urls and self.excluded_urls.url_disabled(url):
        #     return await self.app(scope, receive, send)

        try:
            request = Request(scope=scope, receive=receive)

            corr_ctx.from_cookies(request.cookies)

            # event collection
            req_body = None
            try:
                req_body = (await request.body()).decode("utf-8")
            finally:
                pass

            server_host, port, http_url = get_host_port_url_tuple(scope)
            query_string = scope.get("query_string")
            if query_string and http_url:
                if isinstance(query_string, bytes):
                    query_string = query_string.decode("utf8")
                http_url += "?" + urllib.parse.unquote(query_string)

            attributes = {
                "http_scheme": scope.get("scheme"),
                "http_host": server_host,
                "host_port": port,
                "http_version": scope.get("http_version"),
                "http_target": scope.get("path"),
            }

            # http_host_value_list = asgi_getter.get(scope, "host")
            # if http_host_value_list:
            #     attributes["http_server_name"] = ",".join(http_host_value_list)
            # http_user_agent = asgi_getter.get(scope, "user-agent")
            # if http_user_agent:
            #     attributes["http_user_agent"] = http_user_agent[0]

            # if "client" in scope and scope["client"] is not None:
            #     attributes[SpanAttributes.NET_PEER_IP] = scope.get("client")[0]
            #     attributes[SpanAttributes.NET_PEER_PORT] = scope.get("client")[1]

            attributes = {k: v for k, v in attributes.items() if v is not None}

            req_method = scope.get("method") or "unknown"
            req_url = remove_url_credentials(http_url)
            self.write_queue.put(NetworkInEventPayload(
                request_method=req_method,
                request_url=req_url,
                request_headers=dict(request.headers.items()),
                request_payload=str(req_body),
            ))

            response: Response = await self.app(scope, receive, send)

            # collect response
            # if scope["type"] == "http":
            #     target = _censored_url(scope)

            #     duration = max(round((default_timer() - start) * 1000), 0)
            #     request_size = asgi_getter.get(scope, "content-length")
            #     if request_size:
            #         try:
            #             request_size_amount = int(request_size[0])
            #         except ValueError:
            #             pass

            if response is not None:
                resp_body = await response.body()
                self.write_queue.put(NetworkOutEventPayload(
                    request_method=req_method,
                    request_url=req_url,
                    request_headers=dict(response.headers.items()),
                    request_payload=str(resp_body),
                ))
        finally:
            pass



class StarletteInstrumentor(BaseCollector):
    """An instrumentor for starlette

    See `BaseInstrumentor`
    """

    _original_starlette = None

    # TODO: we shouldnt need to use this
    # def instrument_app(self, app: applications.Starlette):
    #     """Instrument an uninstrumented Starlette application."""
    #     if not getattr(app, "is_instrumented_by_eave", False):
    #         app.add_middleware(
    #             EaveASGIMiddleware,
    #             self.write_queue
    #         )
    #         app.is_instrumented_by_eave = True

    #         # adding apps to set for uninstrumenting
    #         if app not in _InstrumentedStarlette._instrumented_starlette_apps:
    #             _InstrumentedStarlette._instrumented_starlette_apps.add(app)

    def uninstrument_app(self, app: applications.Starlette):
        app.user_middleware = [x for x in app.user_middleware if x.cls is not EaveASGIMiddleware]
        app.middleware_stack = app.build_middleware_stack()
        app.is_instrumented_by_eave = False # type: ignore

    def instrumentation_dependencies(self) -> list[str]:
        return ["starlette"]

    def instrument(self, **kwargs):
        self._original_starlette = applications.Starlette
        applications.Starlette = self._wrap_instrummentor()

    def uninstrument(self, **kwargs):
        """uninstrumenting all created apps by user"""
        for instance in _InstrumentedStarlette._instrumented_starlette_apps:
            self.uninstrument_app(instance)
        _InstrumentedStarlette._instrumented_starlette_apps.clear()
        applications.Starlette = self._original_starlette

    def _wrap_instrummentor(self):
        @wraps(applications.Starlette)
        def _wrapper(*args, **kwargs):
            return _InstrumentedStarlette(self.write_queue, *args, **kwargs)
        return _wrapper

class _InstrumentedStarlette(applications.Starlette):
    _instrumented_starlette_apps = set()

    def __init__(self, write_queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_middleware(EaveASGIMiddleware, write_queue)
        self._is_instrumented_by_eave = True
        # adding apps to set for uninstrumenting
        _InstrumentedStarlette._instrumented_starlette_apps.add(self)

    def __del__(self):
        _InstrumentedStarlette._instrumented_starlette_apps.remove(self)


# def _get_route_details(scope):
#     """
#     Function to retrieve Starlette route from scope.

#     TODO: there is currently no way to retrieve http.route from
#     a starlette application from scope.
#     See: https://github.com/encode/starlette/pull/804

#     Args:
#         scope: A Starlette scope
#     Returns:
#         A string containing the route or None
#     """
#     app = scope["app"]
#     route = None

#     for starlette_route in app.routes:
#         match, _ = starlette_route.matches(scope)
#         if match == Match.FULL:
#             route = starlette_route.path
#             break
#         if match == Match.PARTIAL:
#             route = starlette_route.path
#     return route


# def _get_default_span_details(scope):
#     """
#     Callback to retrieve span name and attributes from scope.

#     Args:
#         scope: A Starlette scope
#     Returns:
#         A tuple of span name and attributes
#     """
#     route = _get_route_details(scope)
#     method = scope.get("method", "")
#     attributes = {}
#     if route:
#         attributes[SpanAttributes.HTTP_ROUTE] = route
#     if method and route:  # http
#         span_name = f"{method} {route}"
#     elif route:  # websocket
#         span_name = route
#     else:  # fallback
#         span_name = method
#     return span_name, attributes
