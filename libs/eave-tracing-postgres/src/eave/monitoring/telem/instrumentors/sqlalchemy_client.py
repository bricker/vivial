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
import threading
from packaging.version import parse as parse_version
from sqlalchemy.engine.base import Engine
from wrapt import wrap_function_wrapper as _w
import os
import re
import weakref
from sqlalchemy.event import (  # pylint: disable=no-name-in-module
    listen,
    remove,
)

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.metrics import get_meter
from opentelemetry.semconv.metrics import MetricInstruments
from opentelemetry.trace import get_tracer
from opentelemetry import trace
from opentelemetry.instrumentation.sqlcommenter_utils import _add_sql_comment
from opentelemetry.instrumentation.utils import _get_opentelemetry_values
from opentelemetry.semconv.trace import NetTransportValues, SpanAttributes
from opentelemetry.trace.status import Status, StatusCode

from eave.core.internal.bigquery.dbchanges import _table_name


def _normalize_vendor(vendor):
    """Return a canonical name for a type of database."""
    if not vendor:
        return "db"  # should this ever happen?

    if "sqlite" in vendor:
        return "sqlite"

    if "postgres" in vendor or vendor == "psycopg2":
        return "postgresql"

    return vendor


def _wrap_create_async_engine(tracer, connections_usage, enable_commenter=False, commenter_options=None):
    # pylint: disable=unused-argument
    def _wrap_create_async_engine_internal(func, module, args, kwargs):
        """Trace the SQLAlchemy engine, creating an `EngineTracer`
        object that will listen to SQLAlchemy events.
        """
        engine = func(*args, **kwargs)
        EngineTracer(
            tracer,
            engine.sync_engine,
            connections_usage,
            enable_commenter,
            commenter_options,
        )
        return engine

    return _wrap_create_async_engine_internal


def _wrap_create_engine(tracer, connections_usage, enable_commenter=False, commenter_options=None):
    def _wrap_create_engine_internal(func, _module, args, kwargs):
        """Trace the SQLAlchemy engine, creating an `EngineTracer`
        object that will listen to SQLAlchemy events.
        """
        engine = func(*args, **kwargs)
        EngineTracer(
            tracer,
            engine,
            connections_usage,
            enable_commenter,
            commenter_options,
        )
        return engine

    return _wrap_create_engine_internal


def _wrap_connect(tracer):
    # pylint: disable=unused-argument
    def _wrap_connect_internal(func, module, args, kwargs):
        with tracer.start_as_current_span("connect", kind=trace.SpanKind.CLIENT) as span:
            if span.is_recording():
                attrs, _ = _get_attributes_from_url(module.url)
                span.set_attributes(attrs)
                span.set_attribute(SpanAttributes.DB_SYSTEM, _normalize_vendor(module.name))
            return func(*args, **kwargs)

    return _wrap_connect_internal


class EngineTracer:
    _remove_event_listener_params = []

    def __init__(
        self,
        tracer,
        engine,
        connections_usage,
        enable_commenter=False,
        commenter_options=None,
    ):
        self.tracer = tracer
        self.connections_usage = connections_usage
        self.vendor = _normalize_vendor(engine.name)
        self.enable_commenter = enable_commenter
        self.commenter_options = commenter_options if commenter_options else {}
        self._engine_attrs = _get_attributes_from_engine(engine)
        self._leading_comment_remover = re.compile(r"^/\*.*?\*/")
        
        self._register_event_listener(engine, "before_cursor_execute", self._before_cur_exec, retval=True)
        self._register_event_listener(engine, "after_cursor_execute", _after_cur_exec)
        # self._register_event_listener(engine, "before_cursor_execute", self._cur_exec_wrapper, retval=True)
        # self._register_event_listener(engine, "after_cursor_execute", self._cur_exec_wrapper)
        self._register_event_listener(engine, "do_execute", self._do_execute_handler)
        self._register_event_listener(engine, "handle_error", _handle_error)
        self._register_event_listener(engine, "connect", self._pool_connect)
        self._register_event_listener(engine, "close", self._pool_close)
        self._register_event_listener(engine, "checkin", self._pool_checkin)
        self._register_event_listener(engine, "checkout", self._pool_checkout)
        self._schema_cache = {}

    def _add_idle_to_connection_usage(self, value):
        self.connections_usage.add(
            value,
            attributes={
                **self._engine_attrs,
                "state": "idle",
            },
        )

    def _add_used_to_connection_usage(self, value):
        self.connections_usage.add(
            value,
            attributes={
                **self._engine_attrs,
                "state": "used",
            },
        )

    def _pool_connect(self, _dbapi_connection, _connection_record):
        self._add_idle_to_connection_usage(1)

    def _pool_close(self, _dbapi_connection, _connection_record):
        self._add_idle_to_connection_usage(-1)

    # Called when a connection returns to the pool.
    def _pool_checkin(self, _dbapi_connection, _connection_record):
        self._add_used_to_connection_usage(-1)
        self._add_idle_to_connection_usage(1)

    # Called when a connection is retrieved from the Pool.
    def _pool_checkout(self, _dbapi_connection, _connection_record, _connection_proxy):
        self._add_idle_to_connection_usage(-1)
        self._add_used_to_connection_usage(1)

    @classmethod
    def _register_event_listener(cls, target, identifier, func, *args, **kw):
        listen(target, identifier, func, *args, **kw)
        cls._remove_event_listener_params.append((weakref.ref(target), identifier, func))

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

    def _exec_cur_wrapper(self):
        pass

    def _do_execute_handler(self, cursor, statement: str, parameters, context):
        result = cursor.execute("select 1")
        print(result)

    def _before_cur_exec(self, conn: sqlalchemy.Connection, cursor: sqlalchemy.CursorResult, statement, params, context, _executemany):
        attrs, found = _get_attributes_from_url(conn.engine.url)
        if not found:
            attrs = _get_attributes_from_cursor(self.vendor, cursor, attrs)

        db_name = attrs.get(SpanAttributes.DB_NAME, "")
        table_name = _table_name(statement) # TODO: dont import this
        op = self._operation_name(statement)


        # result = conn.exec_driver_sql("select 1")
        # print(list(result))

        span = self.tracer.start_span(
            self._operation_name(statement),
            kind=trace.SpanKind.CLIENT,
        )
        with trace.use_span(span, end_on_exit=False):
            if span.is_recording():
                span.set_attribute(SpanAttributes.DB_STATEMENT, statement)
                span.set_attribute(SpanAttributes.DB_SYSTEM, self.vendor)
                span.set_attribute(SpanAttributes.DB_NAME, db_name)

                # NOTE: manually added this
                attr_params = list(map(str, params))
                span.set_attribute("db.params.values", attr_params)
                span.set_attribute("db.structure", "SQL")  # TODO: use enums/constants
                # self._populate_schema_cache(conn)
                # if table_name:
                #     span.set_attribute(SpanAttributes.DB_SQL_TABLE, table_name)

                #     cols = self._columns_from_statement(table_name, statement, conn)
                #     span.set_attribute("db.params.columns", cols)

                # if op:
                #     span.set_attribute(SpanAttributes.DB_OPERATION, op)

                for key, value in attrs.items():
                    span.set_attribute(key, value)
            if self.enable_commenter:
                commenter_data = {
                    "db_driver": conn.engine.driver,
                    # Driver/framework centric information.
                    "db_framework": f"sqlalchemy:{"__version__"}",
                }

                if self.commenter_options.get("opentelemetry_values", True):
                    commenter_data.update(**_get_opentelemetry_values())

                # Filter down to just the requested attributes.
                commenter_data = {k: v for k, v in commenter_data.items() if self.commenter_options.get(k, True)}

                statement = _add_sql_comment(statement, **commenter_data)

        context._otel_span = span

        return statement, params

    def _operation_name(self, statement) -> str | None:
        parts = self._leading_comment_remover.sub("", statement).split()
        if len(parts) == 0:
            return None
        else:
            return parts[0]

    # def _populate_schema_cache(self, conn) -> None:
    #     metadata = sqlalchemy.MetaData()

    #     # this fetches all tables metadata
    #     metadata.reflect(bind=conn)

    #     # populate cache
    #     for table_name, table in metadata.tables.items():
    #         self._schema_cache[table_name] = table


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
            attrs[SpanAttributes.NET_TRANSPORT] = NetTransportValues.OTHER.value
            if info.port:
                # postgresql enforces this pattern on all socket names
                attrs[SpanAttributes.NET_PEER_NAME] = os.path.join(info.host, f".s.PGSQL.{info.port}")
        else:
            attrs[SpanAttributes.NET_TRANSPORT] = NetTransportValues.IP_TCP.value
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

    attrs["pool.name"] = getattr(getattr(engine, "pool", None), "logging_name", None) or _get_connection_string(engine)

    return attrs


class SQLAlchemyInstrumentor(BaseInstrumentor):
    """An instrumentor for SQLAlchemy
    See `BaseInstrumentor`
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return ["sqlalchemy"]  # _instruments

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
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(
            __name__,
            "0",  # __version__,
            tracer_provider,
            schema_url="https://opentelemetry.io/schemas/1.11.0",
        )

        meter_provider = kwargs.get("meter_provider")
        meter = get_meter(
            __name__,
            "0",  # __version__,
            meter_provider,
            schema_url="https://opentelemetry.io/schemas/1.11.0",
        )

        connections_usage = meter.create_up_down_counter(
            name=MetricInstruments.DB_CLIENT_CONNECTIONS_USAGE,
            unit="connections",
            description="The number of connections that are currently in state described by the state attribute.",
        )

        enable_commenter = kwargs.get("enable_commenter", False)
        commenter_options = kwargs.get("commenter_options", {})

        _w(
            "sqlalchemy",
            "create_engine",
            _wrap_create_engine(tracer, connections_usage, enable_commenter, commenter_options),
        )
        _w(
            "sqlalchemy.engine",
            "create_engine",
            _wrap_create_engine(tracer, connections_usage, enable_commenter, commenter_options),
        )
        _w(
            "sqlalchemy.engine.base",
            "Engine.connect",
            _wrap_connect(tracer),
        )
        if parse_version(sqlalchemy.__version__).release >= (1, 4):
            _w(
                "sqlalchemy.ext.asyncio",
                "create_async_engine",
                _wrap_create_async_engine(
                    tracer,
                    connections_usage,
                    enable_commenter,
                    commenter_options,
                ),
            )
        if kwargs.get("engine") is not None:
            return EngineTracer(
                tracer,
                kwargs.get("engine"),
                connections_usage,
                kwargs.get("enable_commenter", False),
                kwargs.get("commenter_options", {}),
            )
        if kwargs.get("engines") is not None and isinstance(kwargs.get("engines"), Sequence):
            return [
                EngineTracer(
                    tracer,
                    engine,
                    connections_usage,
                    kwargs.get("enable_commenter", False),
                    kwargs.get("commenter_options", {}),
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
