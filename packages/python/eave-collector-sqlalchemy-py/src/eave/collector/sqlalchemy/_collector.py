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

from typing import Any, Collection, Mapping, Tuple, Union
from collections.abc import Sequence
from eave.collector.logger import EAVE_LOGGER
import sqlalchemy
from sqlalchemy.engine.interfaces import DBAPICursor, _DBAPIAnyExecuteParams, _CoreMultiExecuteParams, _CoreSingleExecuteParams, _ExecuteOptions
from sqlalchemy.util import immutabledict
import sqlparse
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

from eave.core.internal.bigquery.dbchanges import _operation_name, _table_name

def _normalize_vendor(vendor):
    """Return a canonical name for a type of database."""
    if not vendor:
        return "db"  # should this ever happen?

    if "sqlite" in vendor:
        return "sqlite"

    if "postgres" in vendor or vendor == "psycopg2":
        return "postgresql"

    return vendor


class SQLAlchemyCollector:
    _remove_event_listener_params = []

    def __init__(
        self,
        engine,
    ):
        self.vendor = _normalize_vendor(engine.name)

        self._register_event_listener(engine, "before_cursor_execute", self._before_cur_exec, retval=True)
        self._register_event_listener(engine, "after_cursor_execute", self._after_cur_exec)

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

    # def _before_cur_exec_2(self, conn: sqlalchemy.Connection, cursor: DBAPICursor, statement: str, parameters: _DBAPIAnyExecuteParams, context: sqlalchemy.ExecutionContext | None, executemany: bool) ->  Tuple[str, _DBAPIAnyExecuteParams] | None:
    #     pass

    # def _after_cur_exec_2(self, conn: sqlalchemy.Connection, cursor: DBAPICursor, statement: str, parameters: _DBAPIAnyExecuteParams, context: sqlalchemy.ExecutionContext | None, executemany: bool) -> None:
    #     print(_get_affected_rows(cursor, statement, parameters))

    def _after_cur_exec(self, conn: sqlalchemy.Connection, cursor: DBAPICursor, statement: str, parameters: _DBAPIAnyExecuteParams, context: sqlalchemy.ExecutionContext | None, executemany: bool) -> None:
        print(_get_affected_rows(cursor, statement, parameters))
        print()
        span = getattr(context, "_otel_span", None)
        if span is None:
            return

        span.end()

    def _before_cur_exec(self, conn: sqlalchemy.Connection, cursor: DBAPICursor, statement: str, parameters: _DBAPIAnyExecuteParams, context: sqlalchemy.ExecutionContext, executemany: bool) -> Tuple[str, _DBAPIAnyExecuteParams] | None:
        db_name = conn.engine.url.database
        if not db_name:
            try:
                db_name = cursor.connection.info.dbname
            except AttributeError:
                # db name not available
                EAVE_LOGGER.warning("Could not resolve database name.")
                db_name = "unknown"
                _operation_name("")

        print(statement)
        print(_get_affected_rows(cursor, statement, parameters))

        return statement, parameters


    # def _populate_schema_cache(self, conn) -> None:
    #     metadata = sqlalchemy.MetaData()

    #     # this fetches all tables metadata
    #     metadata.reflect(bind=conn)

    #     # populate cache
    #     for table_name, table in metadata.tables.items():
    #         self._schema_cache[table_name] = table


def _sub_params(statement, params) -> str:
    new_statement = []
    i = 0
    for chunk in statement.split():
        # TODO: ($1::VARCHAR, $2::TIMESTAMP WITHOUT TIME ZONE)
        if chunk[0] == "$" and i < len(params):
            new_statement.append(str(params[i]))
            i += 1
        else:
            new_statement.append(chunk)
    ret = " ".join(new_statement)
    print(ret)
    return ret

def _get_affected_rows(cursor: DBAPICursor, statement: str, params: _DBAPIAnyExecuteParams) -> Sequence[Any] | None:
    """
    extract where clause from statement and use to fetch the rows that will be affected by statement

    NOTE: possibility of sql injection weakness
    """
    s = _sub_params(statement, params)
    where_clauses = [str(t) for t in sqlparse.parse(s)[0].tokens if isinstance(t, sqlparse.sql.Where)]
    if len(where_clauses) > 0:
        table_name = _table_name(statement) # TODO: dont import this
        if table_name:
            # TODO: params values not part of where clause; need to sub all params back into statement first
            stmt=f"select * from {table_name} {where_clauses[0].strip()}"
            print(stmt)
            cursor.execute(stmt)
            result = cursor.fetchall()
            return result



