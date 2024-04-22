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
import time
import asyncpg
import weakref
from collections.abc import Sequence
from typing import Any, Callable, Mapping, Tuple, Union

from eave.collectors.core.collector import BaseCollector
from eave.collectors.core.datastructures import DatabaseEventPayload, DatabaseOperation, DatabaseStructure, EventType
from eave.collectors.core.sql_util import SQLStatementInspector
from eave.collectors.core.write_queue import BatchWriteQueue, QueueParams
from eave.collectors.sqlalchemy.private.util import normalize_vendor
from sqlalchemy.ext.asyncio import AsyncEngine
import sqlparse
from eave.collectors.logging import EAVE_LOGGER

import sqlalchemy
from sqlalchemy.engine.interfaces import (
    DBAPICursor,
    _DBAPIAnyExecuteParams,
)
from sqlalchemy.event import (
    listen,
    remove,
)

import sqlglot
from sqlglot import exp

type SupportedEngine = sqlalchemy.Engine | AsyncEngine

class SQLAlchemyCollector(BaseCollector):
    _event_listeners: list[tuple[weakref.ReferenceType[sqlalchemy.Engine], str, Callable[..., Any]]]
    _db_metadata: sqlalchemy.MetaData | None

    def __init__(
        self,
        credentials: str | None = None
    ) -> None:
        super().__init__(event_type=EventType.dbevent, credentials=credentials)

        self._event_listeners = []
        self._db_metadata = None

    async def start(self, engine: SupportedEngine) -> None:
        if not self.enabled:
            self._db_metadata = await self._load_metadata(engine=engine)

            sync_engine = engine.sync_engine if isinstance(engine, AsyncEngine) else engine
            self._register_engine_event_listener(sync_engine=sync_engine, event_name="before_cursor_execute", fn=self._before_cursor_execute_handler, retval=True)
            self._register_engine_event_listener(sync_engine=sync_engine, event_name="after_cursor_execute", fn=self._after_cursor_execute_handler)

        super().start_base()

    def stop(self) -> None:
        super().stop_base()
        self._db_metadata = None
        self._remove_all_event_listeners()

    async def _load_metadata(self, engine: SupportedEngine) -> sqlalchemy.MetaData:
        metadata = sqlalchemy.MetaData()

        if isinstance(engine, AsyncEngine):
            async with engine.connect() as aconn:
                await aconn.run_sync(metadata.reflect)
        else:
            with engine.connect() as conn:
                metadata.reflect(conn)

        return metadata

    def _register_engine_event_listener(self, sync_engine: sqlalchemy.Engine, event_name: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        self._event_listeners.append((
            weakref.ref(sync_engine),
            event_name,
            fn,
        ))
        listen(target=sync_engine, identifier=event_name, fn=fn, *args, **kwargs)

    def _remove_all_event_listeners(self) -> None:
        for (
            weak_ref_target,
            event_name,
            fn,
        ) in self._event_listeners:
            # Remove an event listener only if saved weak reference points to an object
            # which has not been garbage collected
            if (target := weak_ref_target()) is not None:
                remove(target=target, identifier=event_name, fn=fn)

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
        if not self.enabled:
            return None

        db_name = conn.engine.url.database
        if not db_name:
            try:
                db_name = cursor.connection.info.dbname
            except AttributeError:
                # db name not available
                EAVE_LOGGER.warning("Could not resolve database name.")
                db_name = "unknown"

        # # print("statement >>", statement)
        # # print("db_name >>", db_name)
        # # print()
        # records: list[dict[str, Any]] = []

        # inspector = SQLStatementInspector(statement=statement)

        # operation = inspector.get_operation()
        # tablename = inspector.get_table_name()

        # """
        # Parameters type resolves to:
        #     Union[
        #         Sequence[Any],
        #         Mapping[str, Any]
        #         Sequence[Sequence[Any]],
        #         Sequence[Mapping[str, Any]],
        #     ]

        #     Reminder that strings are Sequences! 🥲
        # """

        # match operation:
        #     case DatabaseOperation.INSERT:
        #         insert_cols = inspector.get_insert_cols()
        #         if insert_cols is None and table is not None:
        #             insert_cols = [c.name for c in table.columns]

        #         if insert_cols is not None:
        #             if isinstance(parameters, (list, tuple)):
        #                 if len(parameters) > 0:
        #                     p0: Sequence[Any] | Mapping[str, Any] | Any = parameters[0]
        #                     if isinstance(p0, (list, tuple)):
        #                         raise NotImplementedError("Unhandled parameters type")
        #                     elif isinstance(p0, dict):
        #                         raise NotImplementedError("Unhandled parameters type")
        #                     else:
        #                         record: dict[str, Any] = {}
        #                         for idx, colname in enumerate(insert_cols):
        #                             # FIXME: This makes the assumption that the number and order of parameters exactly matches the number of columns
        #                             record[colname] = parameters[idx]

        #                         records.append(record)

        #             elif isinstance(parameters, dict):
        #                 # Mapping[str, Any]
        #                 # FIXME: In this case, what exactly is parameters?
        #                 records.append(parameters)

        #             else:
        #                 raise NotImplementedError("Unexpected parameters type")

        #     case DatabaseOperation.UPDATE:
        #         update_cols = inspector.get_update_cols()
        #         if update_cols is not None:
        #             if isinstance(parameters, (list, tuple)):
        #                 if len(parameters) > 0:
        #                     p0: Sequence[Any] | Mapping[str, Any] | Any = parameters[0]
        #                     if isinstance(p0, (list, tuple)):
        #                         raise NotImplementedError("Unhandled parameters type")
        #                     elif isinstance(p0, dict):
        #                         raise NotImplementedError("Unhandled parameters type")
        #                     else:
        #                         record: dict[str, Any] = {}
        #                         for idx, colname in enumerate(insert_cols):
        #                             # FIXME: This makes the assumption that the number and order of parameters exactly matches the number of columns
        #                             record[colname] = parameters[idx]

        #                         records.append(record)

        #             elif isinstance(parameters, dict):
        #                 # Mapping[str, Any]
        #                 # FIXME: In this case, what exactly is parameters?
        #                 records.append(parameters)

        #             else:
        #                 raise NotImplementedError("Unexpected parameters type")

        #     case DatabaseOperation.DELETE:
        #         pass
        #     case DatabaseOperation.SELECT:
        #         pass
        #     case _:
        #         pass

        parsed_statement = sqlglot.parse_one(statement).find(exp.DML)

        records: list[dict[str, Any]] = []

        if parsed_statement:
            table_expr = parsed_statement.find(exp.Table)

            if isinstance(parsed_statement, exp.Insert):
                pass
                # if table_expr:
                #     insert_cols = [e.name for e in table_expr.iter_expressions() if isinstance(e, exp.Identifier)]
                #     if len(insert_cols) == 0:
                #         if self._db_metadata:
                #             table_metadata = self._db_metadata.tables.get(table_expr.name, None)
                #             if table_metadata is not None:
                #                 insert_cols = [c.name for c in table_metadata.columns]

                # if values_expr := parsed_statement.find(exp.Values):
                #     if tuple_expr := next((e for e in values_expr.iter_expressions() if isinstance(e, exp.Tuple)), None):
                #         colum_exprs = tuple_expr.find_all(exp.Column)

            elif isinstance(parsed_statement, exp.Update):
                pass
            elif isinstance(parsed_statement, exp.Delete):
                pass
            elif isinstance(parsed_statement, exp.Select):
                pass
            else:
                    raise ValueError("Unsuppored statement type")


        # payload = DatabaseEventPayload(
        #     statement=statement,
        #     db_name=db_name,
        #     table_name=tablename,
        #     operation=operation,
        #     timestamp=time.time(),
        #     db_structure=DatabaseStructure.SQL,
        #     parameters=parameters,
        #     records=records,
        # )

        # self.write_queue.put(payload)

        # print(self._get_affected_rows(cursor=cursor, statement=statement, parameters=parameters))
        return statement, parameters

    # async def _load_statement_attributes(self, conn: sqlalchemy.Connection, statement: str) -> None:
    #     if conn._dbapi_connection:
    #         dconn: asyncpg.Connection | None = conn._dbapi_connection.driver_connection
    #         if dconn:
    #             p = await dconn.prepare(statement)
    #             print(p.get_attributes())

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
        if not self.enabled:
            return None

        # print(">>> AFTER CURSOR EXECUTE <<<")
        # print("==================")
        # print()
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
