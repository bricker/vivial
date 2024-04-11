# adapted from https://github.com/open-telemetry/opentelemetry-python-contrib/blob/main/instrumentation/opentelemetry-instrumentation-sqlalchemy/src/opentelemetry/instrumentation/sqlalchemy/__init__.py

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

from typing import Collection
from collections.abc import Sequence
import sqlalchemy
from packaging.version import parse as parse_version
from sqlalchemy.engine.base import Engine
from wrapt import wrap_function_wrapper as _w

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.metrics import get_meter
from opentelemetry.semconv.metrics import MetricInstruments
from opentelemetry.trace import get_tracer


import os
import re
import weakref

from sqlalchemy.event import (  # pylint: disable=no-name-in-module
    listen,
    remove,
)

from opentelemetry import trace
from opentelemetry.instrumentation.sqlcommenter_utils import _add_sql_comment
from opentelemetry.instrumentation.utils import _get_opentelemetry_values
from opentelemetry.semconv.trace import NetTransportValues, SpanAttributes
from opentelemetry.trace.status import Status, StatusCode


def _normalize_vendor(vendor):
    """Return a canonical name for a type of database."""
    if not vendor:
        return "db"  # should this ever happen?

    if "sqlite" in vendor:
        return "sqlite"

    if "postgres" in vendor or vendor == "psycopg2":
        return "postgresql"

    return vendor


def _wrap_create_async_engine():
    # pylint: disable=unused-argument
    def _wrap_create_async_engine_internal(func, module, args, kwargs):
        """Trace the SQLAlchemy engine, creating an `EngineTracer`
        object that will listen to SQLAlchemy events.
        """
        engine = func(*args, **kwargs)
        EngineTracer(
            engine.sync_engine,
        )
        return engine

    return _wrap_create_async_engine_internal


def _wrap_create_engine():
    def _wrap_create_engine_internal(func, _module, args, kwargs):
        """Trace the SQLAlchemy engine, creating an `EngineTracer`
        object that will listen to SQLAlchemy events.
        """
        engine = func(*args, **kwargs)
        EngineTracer(
            engine,
        )
        return engine

    return _wrap_create_engine_internal


def _wrap_connect(tracer):
    # pylint: disable=unused-argument
    def _wrap_connect_internal(func, module, args, kwargs):
        with tracer.start_as_current_span(
            "connect", kind=trace.SpanKind.CLIENT
        ) as span:
            if span.is_recording():
                attrs, _ = _get_attributes_from_url(module.url)
                span.set_attributes(attrs)
                span.set_attribute(
                    SpanAttributes.DB_SYSTEM, _normalize_vendor(module.name)
                )
            return func(*args, **kwargs)

    return _wrap_connect_internal


class EngineTracer:
    _remove_event_listener_params = []

    def __init__(
        self,
        engine,
    ):
        self.vendor = _normalize_vendor(engine.name)
        self._engine_attrs = _get_attributes_from_engine(engine)
        self._leading_comment_remover = re.compile(r"^/\*.*?\*/")

        self._register_event_listener(
            engine, "before_cursor_execute", self._before_cur_exec, retval=True
        )
        self._register_event_listener(
            engine, "after_cursor_execute", _after_cur_exec
        )
        self._register_event_listener(engine, "handle_error", _handle_error)

    @classmethod
    def _register_event_listener(cls, target, identifier, func, *args, **kw):
        listen(target, identifier, func, *args, **kw)
        cls._remove_event_listener_params.append(
            (weakref.ref(target), identifier, func)
        )

    @classmethod
    def remove_all_event_listeners(cls):
        for (
            weak_ref_target,
            identifier,
            func,
        ) in cls._remove_event_listener_params:
            # Remove an event listener only if saved weak reference points to an object
            # which has not been garbage collected
            if weak_ref_target() is not None:
                remove(weak_ref_target(), identifier, func)
        cls._remove_event_listener_params.clear()

    def _operation_name(self, db_name, statement):
        parts = []
        if isinstance(statement, str):
            # otel spec recommends against parsing SQL queries. We are not trying to parse SQL
            # but simply truncating the statement to the first word. This covers probably >95%
            # use cases and uses the SQL statement in span name correctly as per the spec.
            # For some very special cases it might not record the correct statement if the SQL
            # dialect is too weird but in any case it shouldn't break anything.
            # Strip leading comments so we get the operation name.
            parts.append(
                self._leading_comment_remover.sub("", statement).split()[0]
            )
        if db_name:
            parts.append(db_name)
        if not parts:
            return self.vendor
        return " ".join(parts)

    def _before_cur_exec(
        self, conn, cursor, statement, params, context, _executemany
    ):
        attrs, found = _get_attributes_from_url(conn.engine.url)
        if not found:
            attrs = _get_attributes_from_cursor(self.vendor, cursor, attrs)

        db_name = attrs.get(SpanAttributes.DB_NAME, "")
 
        # TODO: wtf to replace span with...
        span.set_attribute(SpanAttributes.DB_STATEMENT, statement)
        span.set_attribute(SpanAttributes.DB_SYSTEM, self.vendor)

        span.set_attribute("db.params", str(params))
        span.set_attribute("db.operation", self._operation_name(db_name, statement))

        for key, value in attrs.items():
            span.set_attribute(key, value)

        return statement, params


# pylint: disable=unused-argument
def _after_cur_exec(conn, cursor, statement, params, context, executemany):
    span = getattr(context, "_otel_span", None)
    if span is None:
        return

    span.end()


def _handle_error(context):
    span = getattr(context.execution_context, "_otel_span", None)
    if span is None:
        return

    if span.is_recording():
        span.set_status(
            Status(
                StatusCode.ERROR,
                str(context.original_exception),
            )
        )
    span.end()


def _get_attributes_from_url(url):
    """Set connection tags from the url. return true if successful."""
    attrs = {}
    if url.host:
        attrs[SpanAttributes.NET_PEER_NAME] = url.host
    if url.port:
        attrs[SpanAttributes.NET_PEER_PORT] = url.port
    if url.database:
        attrs[SpanAttributes.DB_NAME] = url.database
    if url.username:
        attrs[SpanAttributes.DB_USER] = url.username
    return attrs, bool(url.host)


def _get_attributes_from_cursor(vendor, cursor, attrs):
    """Attempt to set db connection attributes by introspecting the cursor."""
    if vendor == "postgresql":
        info = getattr(getattr(cursor, "connection", None), "info", None)
        if not info:
            return attrs

        attrs[SpanAttributes.DB_NAME] = info.dbname
        is_unix_socket = info.host and info.host.startswith("/")

        if is_unix_socket:
            attrs[
                SpanAttributes.NET_TRANSPORT
            ] = NetTransportValues.OTHER.value
            if info.port:
                # postgresql enforces this pattern on all socket names
                attrs[SpanAttributes.NET_PEER_NAME] = os.path.join(
                    info.host, f".s.PGSQL.{info.port}"
                )
        else:
            attrs[
                SpanAttributes.NET_TRANSPORT
            ] = NetTransportValues.IP_TCP.value
            attrs[SpanAttributes.NET_PEER_NAME] = info.host
            if info.port:
                attrs[SpanAttributes.NET_PEER_PORT] = int(info.port)
    return attrs


def _get_connection_string(engine):
    drivername = engine.url.drivername or ""
    host = engine.url.host or ""
    port = engine.url.port or ""
    database = engine.url.database or ""
    return f"{drivername}://{host}:{port}/{database}"


def _get_attributes_from_engine(engine):
    """Set metadata attributes of the database engine"""
    attrs = {}

    attrs["pool.name"] = getattr(
        getattr(engine, "pool", None), "logging_name", None
    ) or _get_connection_string(engine)

    return attrs

class SQLAlchemyInstrumentor(BaseInstrumentor):
    """An instrumentor for SQLAlchemy
    See `BaseInstrumentor`
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["sqlalchemy"] #_instruments

    def _instrument(self, **kwargs):
        """Instruments SQLAlchemy engine creation methods and the engine
        if passed as an argument.

        Args:
            **kwargs: Optional arguments
                ``engine``: a SQLAlchemy engine instance
                ``engines``: a list of SQLAlchemy engine instances
                ``tracer_provider``: a TracerProvider, defaults to global
                ``meter_provider``: a MeterProvider, defaults to global
                ``enable_commenter``: bool to enable sqlcommenter, defaults to False
                ``commenter_options``: dict of sqlcommenter config, defaults to {}

        Returns:
            An instrumented engine if passed in as an argument or list of instrumented engines, None otherwise.
        """
        _w(
            "sqlalchemy",
            "create_engine",
            _wrap_create_engine(),
        )
        _w(
            "sqlalchemy.engine",
            "create_engine",
            _wrap_create_engine(),
        )
        _w(
            "sqlalchemy.engine.base",
            "Engine.connect",
            _wrap_connect(),
        )
        if parse_version(sqlalchemy.__version__).release >= (1, 4):
            _w(
                "sqlalchemy.ext.asyncio",
                "create_async_engine",
                _wrap_create_async_engine(),
            )
        if kwargs.get("engine") is not None:
            return EngineTracer(
                kwargs.get("engine"),
            )
        if kwargs.get("engines") is not None and isinstance(
            kwargs.get("engines"), Sequence
        ):
            return [
                EngineTracer(
                    engine,
                )
                for engine in kwargs.get("engines", [])
            ]

        return None

    def _uninstrument(self, **kwargs):
        unwrap(sqlalchemy, "create_engine")
        unwrap(sqlalchemy.engine, "create_engine")
        unwrap(Engine, "connect")
        if parse_version(sqlalchemy.__version__).release >= (1, 4):
            unwrap(sqlalchemy.ext.asyncio, "create_async_engine")
        EngineTracer.remove_all_event_listeners()