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

import time
import urllib.parse
from collections.abc import Callable
from functools import wraps

import starlette.types
from asgiref.compatibility import guarantee_single_callable
from starlette import applications
from starlette.datastructures import MutableHeaders
from starlette.requests import Request

# from starlette.routing import Match
from eave.collectors.core.base_collector import BaseCollector
from eave.collectors.core.correlation_context import CORR_CTX
from eave.collectors.core.datastructures import HttpServerEventPayload

# from timeit import default_timer
from eave.collectors.core.logging import EAVE_LOGGER
from eave.collectors.core.write_queue import WriteQueue

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


def get_host_port_url_tuple(scope: starlette.types.Scope) -> tuple[str, int, str]:
    """Returns (host, port, full_url) tuple."""
    server = scope.get("server") or ["0.0.0.0", 80]  # noqa: S104
    port = server[1]
    server_host = server[0] + (":" + str(port) if str(port) != "80" else "")
    full_path = scope.get("root_path", "") + scope.get("path", "")
    http_url = scope.get("scheme", "http") + "://" + server_host + full_path
    return server_host, port, http_url


# def get_default_span_details(scope: starlette.types.Scope) -> str:
#     """
#     Default span name is the HTTP method and URL path, or just the method.
#     https://github.com/open-telemetry/opentelemetry-specification/pull/3165
#     https://opentelemetry.io/docs/reference/specification/trace/semantic_conventions/http/#name

#     Args:
#         scope: the ASGI scope dictionary
#     Returns:
#         a tuple of the span name, and any attributes to attach to the span.
#     """
#     path = scope.get("path", "").strip()
#     method = scope.get("method", "").strip()
#     if method and path:  # http
#         return f"{method} {path}"
#     if path:  # websocket
#         return path
#     return method  # http with no path


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
        app: starlette.types.ASGIApp,
        write_queue: WriteQueue,
    ) -> None:
        self.app = guarantee_single_callable(app)
        self.content_length_header = None
        self.write_queue = write_queue

    async def __call__(
        self, scope: starlette.types.Scope, receive: starlette.types.Receive, send: starlette.types.Send
    ) -> None:
        """The ASGI application

        Args:
            scope: An ASGI environment.
            receive: An awaitable callable yielding dictionaries
            send: An awaitable callable taking a single dictionary as argument.
        """
        # start = default_timer()
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # _, _, url = get_host_port_url_tuple(scope)
        # TODO: offer config options for URL patterns to exclude?
        # if self.excluded_urls and self.excluded_urls.url_disabled(url):
        #     return await self.app(scope, receive, send)

        try:
            request = Request(scope=scope, receive=receive)

            # init ctx
            CORR_CTX.from_cookies(request.cookies)

            # event collection
            # NOTE: this removes ability for further middleware/processing to request streaming by consuming the body
            # TODO: Fix this, it causes hanging later when attempting to read the body.
            req_body = await request.body()

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
            self.write_queue.put(
                HttpServerEventPayload(
                    timestamp=time.time(),
                    request_method=req_method,
                    request_url=req_url,
                    request_headers=dict(request.headers.items()),
                    request_payload=req_body.decode("utf-8"),
                    corr_ctx=CORR_CTX.to_dict(),
                )
            )

            # we need this external header reference to get scope captured in `resonse_interceptor`
            # so that headers can be saved in 1 send message execution and still referenced in
            # a later invocation of the `response_interceptor` function that fires the analytics event.
            # (stored as a list so we can reassign the value w/o reassigning the variable reference)
            headers_ref: list[dict[str, str]] = [{}]

            async def response_interceptor(message: starlette.types.Message) -> None:
                """wrapper to fire analytics events on ASGI response messages"""
                # message definitions per ASGI spec:
                # https://asgi.readthedocs.io/en/latest/specs/www.html#response-start-send-event
                if message["type"] == "http.response.start":
                    headers = MutableHeaders(scope=message)
                    # save current headers for event
                    headers_ref[0] = dict(headers.items())
                    # add our eave ctx cookie to the response
                    for cookie in CORR_CTX.get_updated_values_cookies():
                        headers.append("Set-Cookie", cookie)
                elif message["type"] == "http.response.body":
                    # TODO: Fix this, it needs to check for `more_body=True`
                    # resp_body = None
                    # try:
                    #     resp_body = message["body"].decode("utf-8")
                    # except UnicodeDecodeError:
                    #     pass
                    # self.write_queue.put(
                    #     HttpServerEventPayload(
                    #         timestamp=time.time(),
                    #         request_method=req_method,
                    #         request_url=req_url,
                    #         request_headers=headers_ref[0],
                    #         request_payload=str(resp_body),
                    #         corr_ctx=CORR_CTX.to_dict(),
                    #     )
                    # )

                    # destroy ctx now that we're done with it
                    CORR_CTX.clear()

                await send(message)

            # Then overwrite ASGI receive messages to set the body for all downstream request handlers.
            async def receive_interceptor() -> starlette.types.Message:
                # FIXME: This disregards any other event type (eg http.disconnect)
                # To fix this, this interceptor function should check the type of the original receive event,
                # and return accordingly.
                return {
                    "type": "http.request",
                    "body": req_body,
                    "more_body": False,
                }

            await self.app(scope, receive_interceptor, response_interceptor)

            # if scope["type"] == "http":
            #     target = _censored_url(scope)

            #     duration = max(round((default_timer() - start) * 1000), 0)
            #     request_size = asgi_getter.get(scope, "content-length")
            #     if request_size:
            #         try:
            #             request_size_amount = int(request_size[0])
            #         except ValueError:
            #             pass

        except UnicodeDecodeError as e:
            # ignore json decoding errors
            EAVE_LOGGER.warning(e)
        except Exception as e:
            # Don't prevent the request from going through
            EAVE_LOGGER.exception(e)


class StarletteCollector(BaseCollector):
    _original_starlette = None

    def __init__(self) -> None:
        super().__init__()

    def instrument_app(self, app: applications.Starlette) -> None:
        """instrument specific app instance only"""
        if not getattr(app, "is_instrumented_by_eave", False):
            self.write_queue.start_autoflush()
            app.add_middleware(
                EaveASGIMiddleware,
                write_queue=self.write_queue,
            )
            app.is_instrumented_by_eave = True  # type: ignore

            # adding apps to set for uninstrumenting
            if app not in _InstrumentedStarlette._instrumented_starlette_apps:  # noqa: SLF001
                _InstrumentedStarlette._instrumented_starlette_apps.add(app)  # noqa: SLF001

    def uninstrument_app(self, app: applications.Starlette) -> None:
        app.user_middleware = [x for x in app.user_middleware if x.cls is not EaveASGIMiddleware]
        app.middleware_stack = app.build_middleware_stack()
        app.is_instrumented_by_eave = False  # type: ignore

    def instrument(self) -> None:
        self.write_queue.start_autoflush()
        self._original_starlette = applications.Starlette
        applications.Starlette = self._wrap_instrummentor()

    def uninstrument(self) -> None:
        """uninstrumenting all created apps by user"""
        for instance in _InstrumentedStarlette._instrumented_starlette_apps:  # noqa: SLF001
            self.uninstrument_app(instance)
        _InstrumentedStarlette._instrumented_starlette_apps.clear()  # noqa: SLF001
        applications.Starlette = self._original_starlette

    def _wrap_instrummentor(self) -> Callable:
        @wraps(applications.Starlette)
        def _wrapper(*args, **kwargs) -> applications.Starlette:
            return _InstrumentedStarlette(self.write_queue, *args, **kwargs)

        return _wrapper


class _InstrumentedStarlette(applications.Starlette):
    _instrumented_starlette_apps = set()  # noqa: RUF012

    def __init__(self, write_queue: WriteQueue, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_middleware(EaveASGIMiddleware, write_queue=write_queue)
        self._is_instrumented_by_eave = True
        # adding apps to set for uninstrumenting
        _InstrumentedStarlette._instrumented_starlette_apps.add(self)

    def __del__(self) -> None:
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
