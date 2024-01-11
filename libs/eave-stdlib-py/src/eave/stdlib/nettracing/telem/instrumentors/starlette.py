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
from typing import Collection

from starlette import applications
from starlette.routing import Match

from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.starlette.package import _instruments
from opentelemetry.instrumentation.starlette.version import __version__
from opentelemetry.metrics import get_meter
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import Span
from opentelemetry.util.http import get_excluded_urls

_excluded_urls = get_excluded_urls("STARLETTE")

_ServerRequestHookT = typing.Optional[typing.Callable[[Span, dict], None]]
_ClientRequestHookT = typing.Optional[typing.Callable[[Span, dict], None]]
_ClientResponseHookT = typing.Optional[typing.Callable[[Span, dict], None]]


class StarletteInstrumentor(BaseInstrumentor):
    """An instrumentor for starlette

    See `BaseInstrumentor`
    """

    _original_starlette = None

    @staticmethod
    def instrument_app(
        app: applications.Starlette,
        server_request_hook: _ServerRequestHookT = None,
        client_request_hook: _ClientRequestHookT = None,
        client_response_hook: _ClientResponseHookT = None,
        meter_provider=None,
        tracer_provider=None,
    ):
        """Instrument an uninstrumented Starlette application."""
        meter = get_meter(
            __name__,
            __version__,
            meter_provider,
            schema_url="https://opentelemetry.io/schemas/1.11.0",
        )
        if not getattr(app, "is_instrumented_by_opentelemetry", False):
            app.add_middleware(
                OpenTelemetryMiddleware,
                excluded_urls=_excluded_urls,
                default_span_details=_get_default_span_details,
                server_request_hook=server_request_hook,
                client_request_hook=client_request_hook,
                client_response_hook=client_response_hook,
                tracer_provider=tracer_provider,
                meter=meter,
            )
            app.is_instrumented_by_opentelemetry = True

            # adding apps to set for uninstrumenting
            if app not in _InstrumentedStarlette._instrumented_starlette_apps:
                _InstrumentedStarlette._instrumented_starlette_apps.add(app)

    @staticmethod
    def uninstrument_app(app: applications.Starlette):
        app.user_middleware = [
            x
            for x in app.user_middleware
            if x.cls is not OpenTelemetryMiddleware
        ]
        app.middleware_stack = app.build_middleware_stack()
        app._is_instrumented_by_opentelemetry = False

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        self._original_starlette = applications.Starlette
        _InstrumentedStarlette._tracer_provider = kwargs.get("tracer_provider")
        _InstrumentedStarlette._server_request_hook = kwargs.get(
            "server_request_hook"
        )
        _InstrumentedStarlette._client_request_hook = kwargs.get(
            "client_request_hook"
        )
        _InstrumentedStarlette._client_response_hook = kwargs.get(
            "client_response_hook"
        )
        _InstrumentedStarlette._meter_provider = kwargs.get("_meter_provider")

        applications.Starlette = _InstrumentedStarlette

    def _uninstrument(self, **kwargs):
        """uninstrumenting all created apps by user"""
        for instance in _InstrumentedStarlette._instrumented_starlette_apps:
            self.uninstrument_app(instance)
        _InstrumentedStarlette._instrumented_starlette_apps.clear()
        applications.Starlette = self._original_starlette


class _InstrumentedStarlette(applications.Starlette):
    _tracer_provider = None
    _meter_provider = None
    _server_request_hook: _ServerRequestHookT = None
    _client_request_hook: _ClientRequestHookT = None
    _client_response_hook: _ClientResponseHookT = None
    _instrumented_starlette_apps = set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        meter = get_meter(
            __name__,
            __version__,
            _InstrumentedStarlette._meter_provider,
            schema_url="https://opentelemetry.io/schemas/1.11.0",
        )
        self.add_middleware(
            OpenTelemetryMiddleware,
            excluded_urls=_excluded_urls,
            default_span_details=_get_default_span_details,
            server_request_hook=_InstrumentedStarlette._server_request_hook,
            client_request_hook=_InstrumentedStarlette._client_request_hook,
            client_response_hook=_InstrumentedStarlette._client_response_hook,
            tracer_provider=_InstrumentedStarlette._tracer_provider,
            meter=meter,
        )
        self._is_instrumented_by_opentelemetry = True
        # adding apps to set for uninstrumenting
        _InstrumentedStarlette._instrumented_starlette_apps.add(self)

    def __del__(self):
        _InstrumentedStarlette._instrumented_starlette_apps.remove(self)


def _get_route_details(scope):
    """
    Function to retrieve Starlette route from scope.

    TODO: there is currently no way to retrieve http.route from
    a starlette application from scope.
    See: https://github.com/encode/starlette/pull/804

    Args:
        scope: A Starlette scope
    Returns:
        A string containing the route or None
    """
    app = scope["app"]
    route = None

    for starlette_route in app.routes:
        match, _ = starlette_route.matches(scope)
        if match == Match.FULL:
            route = starlette_route.path
            break
        if match == Match.PARTIAL:
            route = starlette_route.path
    return route


def _get_default_span_details(scope):
    """
    Callback to retrieve span name and attributes from scope.

    Args:
        scope: A Starlette scope
    Returns:
        A tuple of span name and attributes
    """
    route = _get_route_details(scope)
    method = scope.get("method", "")
    attributes = {}
    if route:
        attributes[SpanAttributes.HTTP_ROUTE] = route
    if method and route:  # http
        span_name = f"{method} {route}"
    elif route:  # websocket
        span_name = route
    else:  # fallback
        span_name = method
    return span_name, attributes