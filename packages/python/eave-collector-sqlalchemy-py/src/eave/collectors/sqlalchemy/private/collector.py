import time
import weakref
from collections.abc import Callable
from typing import Any

import sqlalchemy
from sqlalchemy.engine.interfaces import (
    _CoreMultiExecuteParams,
    _CoreSingleExecuteParams,
    _ExecuteOptions,
)
from sqlalchemy.event import (
    listen,
    remove,
)
from sqlalchemy.ext.asyncio import AsyncEngine

from eave.collectors.core.base_database_collector import (
    BaseDatabaseCollector,
    is_column_of_interest,
    is_table_of_interest,
    save_data_of_interest,
)
from eave.collectors.core.correlation_context import corr_ctx
from eave.collectors.core.datastructures import DatabaseEventPayload, DatabaseOperation, DatabaseStructure
from eave.collectors.core.write_queue import WriteQueue

type SupportedEngine = sqlalchemy.Engine | AsyncEngine


class SQLAlchemyCollector(BaseDatabaseCollector):
    _event_listeners: list[tuple[weakref.ReferenceType[sqlalchemy.Engine], str, Callable[..., Any]]]
    _db_metadata: sqlalchemy.MetaData | None

    def __init__(self, *, write_queue: WriteQueue | None = None) -> None:
        super().__init__(write_queue=write_queue)

        self._event_listeners = []
        self._db_metadata = None

    async def start(self, engine: SupportedEngine) -> None:
        if not self.enabled:
            self.run()
            # self._db_metadata = await self._load_metadata(engine=engine)

            sync_engine = engine.sync_engine if isinstance(engine, AsyncEngine) else engine
            self._register_engine_event_listener(
                sync_engine=sync_engine, event_name="before_execute", fn=self._before_execute_handler
            )
            self._register_engine_event_listener(
                sync_engine=sync_engine, event_name="after_execute", fn=self._after_execute_handler
            )

    def stop(self) -> None:
        self._remove_all_event_listeners()
        self.terminate()
        self._db_metadata = None

    # async def _load_metadata(self, engine: SupportedEngine) -> sqlalchemy.MetaData:
    #     metadata = sqlalchemy.MetaData()

    #     if isinstance(engine, AsyncEngine):
    #         async with engine.connect() as aconn:
    #             await aconn.run_sync(metadata.reflect)
    #     else:
    #         with engine.connect() as conn:
    #             metadata.reflect(conn)

    #     return metadata

    def _register_engine_event_listener(
        self, sync_engine: sqlalchemy.Engine, event_name: str, fn: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> None:
        self._event_listeners.append(
            (
                weakref.ref(sync_engine),
                event_name,
                fn,
            )
        )
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

    def _before_execute_handler(
        self,
        conn: sqlalchemy.Connection,
        clauseelement: sqlalchemy.Executable,
        multiparams: _CoreMultiExecuteParams,
        params: _CoreSingleExecuteParams,
        execution_options: _ExecuteOptions,
    ) -> tuple[sqlalchemy.Executable, _CoreMultiExecuteParams, _CoreSingleExecuteParams] | None:
        if clauseelement.is_insert or clauseelement.is_select:
            return

    def _after_execute_handler(
        self,
        conn: sqlalchemy.Connection,
        clauseelement: sqlalchemy.Executable,
        multiparams: list[dict[str, Any]],
        params: dict[str, Any],
        execution_options: _ExecuteOptions,
        result: sqlalchemy.Result[Any],
    ) -> None:
        rparams: list[dict[str, Any]]

        # This assumes that multiparams and params are mutually exclusive
        if len(multiparams) > 0:
            rparams = multiparams
        else:
            rparams = [params]

        tablename = "__unknown"

        if isinstance(clauseelement, (sqlalchemy.Select, sqlalchemy.Insert, sqlalchemy.Update, sqlalchemy.Delete)):
            if isinstance(clauseelement, sqlalchemy.Select):
                # attempt to get table name from a FromClause
                # (this doesnt really work for complex select statements w/ joins)
                from_clause = clauseelement.get_final_froms()
                if len(from_clause) > 0:
                    candidate_name = getattr(from_clause[0], "name", None)
                    if candidate_name is not None:
                        tablename = candidate_name
            elif isinstance(clauseelement.table, sqlalchemy.Table):
                tablename = clauseelement.table.fullname

            if isinstance(clauseelement, sqlalchemy.Select):
                for idx, rparam in enumerate(rparams):
                    compiled_clause = clauseelement.compile()
                    statement_params = rparam or dict(compiled_clause.params)

                    self._save_data_of_interest(tablename, clauseelement, rparam)

                    record = DatabaseEventPayload(
                        timestamp=time.time(),
                        db_structure=DatabaseStructure.SQL,
                        operation=DatabaseOperation.SELECT,
                        db_name=conn.engine.url.database,
                        statement=compiled_clause.string,
                        table_name=tablename,
                        parameters=statement_params,
                        context=corr_ctx.to_dict(),
                    )

                    self.write_queue.put(record)

            if isinstance(clauseelement, sqlalchemy.Insert):
                for idx, rparam in enumerate(rparams):
                    pkeys = None
                    if isinstance(result, sqlalchemy.CursorResult) and len(result.inserted_primary_key_rows) > idx:
                        row = result.inserted_primary_key_rows[idx]
                        pkeys = list(row.tuple())

                    rparam["__primary_key"] = pkeys

                    if pkeys and len(pkeys) > 0:
                        save_data_of_interest(table_name=tablename, column_name=, column_value=str(pkeys[0]))

                    record = DatabaseEventPayload(
                        timestamp=time.time(),
                        db_structure=DatabaseStructure.SQL,
                        operation=DatabaseOperation.INSERT,
                        db_name=conn.engine.url.database,
                        statement=clauseelement.compile().string,
                        table_name=tablename,
                        parameters=rparam,
                        context=corr_ctx.to_dict(),
                    )

                    self.write_queue.put(record)

            elif isinstance(clauseelement, sqlalchemy.Update):
                for idx, rparam in enumerate(rparams):
                    self._save_data_of_interest(tablename, clauseelement, rparam)

                    record = DatabaseEventPayload(
                        timestamp=time.time(),
                        db_structure=DatabaseStructure.SQL,
                        operation=DatabaseOperation.UPDATE,
                        db_name=conn.engine.url.database,
                        statement=clauseelement.compile().string,
                        table_name=tablename,
                        parameters=rparam,
                        context=corr_ctx.to_dict(),
                    )

                    self.write_queue.put(record)

            elif isinstance(clauseelement, sqlalchemy.Delete):
                for idx, rparam in enumerate(rparams):
                    record = DatabaseEventPayload(
                        timestamp=time.time(),
                        db_structure=DatabaseStructure.SQL,
                        operation=DatabaseOperation.DELETE,
                        db_name=conn.engine.url.database,
                        statement=clauseelement.compile().string,
                        table_name=tablename,
                        parameters=rparam,
                        context=corr_ctx.to_dict(),
                    )

                    self.write_queue.put(record)

    def _save_data_of_interest(
        self, tablename: str, clauseelement: sqlalchemy.Select | sqlalchemy.Update, params: dict[str, Any]
    ) -> None:
        """
        If the `tablename` the `clauseelement` is acting on is of interest (e.g. a user table),
        search the statement WHERE clause for a ID column comparison to extract the
        compared ID value from, and save that value to the correlation context.
        """
        if is_table_of_interest(tablename):
            compiled_clause = clauseelement.compile()
            statement_params = params or dict(compiled_clause.params)
            # try to extract column values of interest from where clause
            where_clause = clauseelement.whereclause
            if where_clause is not None:
                # extract terms as list of binary expressions
                if isinstance(where_clause, sqlalchemy.BooleanClauseList):
                    where_clause = list(where_clause)
                else:
                    where_clause = [where_clause]

                for expr in where_clause:
                    if not (isinstance(expr, sqlalchemy.BinaryExpression) and isinstance(expr.left, sqlalchemy.Column)):
                        # we only care about binary expressions comparing columns to a value
                        continue
                    col_name = expr.left.name
                    if is_column_of_interest(col_name):
                        # strip leading colon off param key (e.g. :id_1 -> id_1)
                        param_key = str(expr.right).lstrip(":")
                        param_value = statement_params.get(param_key, None)
                        if param_value is not None:
                            # make sure the field actually corresponds to the table we're interested in
                            field_table = expr.left.table.name
                            save_data_of_interest(table_name=field_table, column_name=col_name, column_value=param_value)
