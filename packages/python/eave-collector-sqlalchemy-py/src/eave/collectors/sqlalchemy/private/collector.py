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

import asyncio
import asyncpg
import weakref
from collections.abc import Sequence
from typing import Any, Callable, Tuple, Union

from eave.collectors.sqlalchemy.private.util import normalize_vendor
from sqlalchemy.ext.asyncio import AsyncEngine
import sqlparse
from eave.collectors.logging import EAVE_LOGGER
from eave.core.internal.bigquery.dbchanges import _operation_name, _table_name

import sqlalchemy
from sqlalchemy.engine.interfaces import (
    DBAPICursor,
    _DBAPIAnyExecuteParams,
)
from sqlalchemy.event import (
    listen,
    remove,
)

type AnyEngine = sqlalchemy.Engine

class SQLAlchemyCollector:
    _event_listeners: list[tuple[weakref.ReferenceType[AnyEngine], str, Callable[..., Any]]]
    _db_metadata: sqlalchemy.MetaData | None
    _running: bool
    _tasks: set[asyncio.Task]

    def __init__(
        self,
    ) -> None:
        self._event_listeners = []
        self._db_metadata = None
        self._running = False
        self._tasks = set()

    async def start(self, engine: AnyEngine) -> None:
        if not self._running:
            await self._load_metadata(engine)
            self._register_engine_event_listener(target=engine, identifier="before_cursor_execute", fn=self._before_cursor_execute_handler, retval=True)
            self._register_engine_event_listener(target=engine, identifier="after_cursor_execute", fn=self._after_cursor_execute_handler)
            self._running = True

    def stop(self) -> None:
        self._remove_all_event_listeners()
        self._running = False

    async def _load_metadata(self, engine: AnyEngine) -> None:
        metadata = sqlalchemy.MetaData()
        metadata.reflect(engine)
        print(metadata)
        # with engine.connect() as conn:
        #     metadata.reflect(bind=engine)
        # self._metadata = metadata

    def _register_engine_event_listener(self, target: AnyEngine, identifier: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        self._event_listeners.append((
            weakref.ref(target),
            identifier,
            fn,
        ))
        listen(target=target, identifier=identifier, fn=fn, *args, **kwargs)

    def _remove_all_event_listeners(self) -> None:
        for (
            weak_ref_target,
            identifier,
            fn,
        ) in self._event_listeners:
            # Remove an event listener only if saved weak reference points to an object
            # which has not been garbage collected
            if (target := weak_ref_target()) is not None:
                remove(target=target, identifier=identifier, fn=fn)

        self._event_listeners.clear()

    def _before_cursor_execute_handler(
        self,
        conn: sqlalchemy.Connection,
        cursor: DBAPICursor,
        statement: str,
        parameters: _DBAPIAnyExecuteParams,
        _context: sqlalchemy.ExecutionContext | None,
        _executemany: bool,  # noqa: FBT001
    ) -> Tuple[str, _DBAPIAnyExecuteParams] | None:
        """
        https://docs.sqlalchemy.org/en/20/core/events.html#sqlalchemy.events.ConnectionEvents.before_cursor_execute
        """
        db_name = conn.engine.url.database
        if not db_name:
            try:
                db_name = cursor.connection.info.dbname
            except AttributeError:
                # db name not available
                EAVE_LOGGER.warning("Could not resolve database name.")
                db_name = "unknown"

        print(statement)
        task = asyncio.create_task(self._load_statement_attributes(conn=conn, statement=statement))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

        # print(self._get_affected_rows(cursor=cursor, statement=statement, parameters=parameters))
        return statement, parameters

    async def _load_statement_attributes(self, conn: sqlalchemy.Connection, statement: str) -> None:
        if conn._dbapi_connection:
            dconn: asyncpg.Connection | None = conn._dbapi_connection.driver_connection
            if dconn:
                p = await dconn.prepare(statement)
                print(p.get_attributes())

    def _after_cursor_execute_handler(
        self,
        conn: sqlalchemy.Connection,
        cursor: DBAPICursor,
        statement: str,
        parameters: _DBAPIAnyExecuteParams,
        context: sqlalchemy.ExecutionContext | None,
        _executemany: bool,  # noqa: FBT001
    ) -> None:
        """
        https://docs.sqlalchemy.org/en/20/core/events.html#sqlalchemy.events.ConnectionEvents.after_cursor_execute
        """
        pass
        # print(self._get_affected_rows(cursor, statement, parameters))
        # print()

    # def _sub_params(self, statement: str, parameters: _DBAPIAnyExecuteParams) -> str:
    #     new_statement = []
    #     i = 0
    #     for chunk in statement.split():
    #         # TODO: ($1::VARCHAR, $2::TIMESTAMP WITHOUT TIME ZONE)
    #         if chunk[0] == "$" and i < len(parameters):
    #             new_statement.append(str(parameters[i]))
    #             i += 1
    #         else:
    #             new_statement.append(chunk)
    #     ret = " ".join(new_statement)
    #     print(ret)
    #     return ret


    # def _get_affected_rows(self, cursor: DBAPICursor, statement: str, parameters: _DBAPIAnyExecuteParams) -> Sequence[Any] | None:
    #     """
    #     extract where clause from statement and use to fetch the rows that will be affected by statement

    #     NOTE: possibility of sql injection weakness
    #     """
    #     s = self._sub_params(statement=statement, parameters=parameters)
    #     where_clauses = [str(t) for t in sqlparse.parse(s)[0].tokens if isinstance(t, sqlparse.sql.Where)]
    #     if len(where_clauses) > 0:
    #         table_name = _table_name(statement)  # TODO: dont import this
    #         if table_name:
    #             # TODO: params values not part of where clause; need to sub all params back into statement first
    #             stmt = f"select * from {table_name} {where_clauses[0].strip()}"
    #             print(stmt)
    #             cursor.execute(stmt)
    #             result = cursor.fetchall()
    #             return result
