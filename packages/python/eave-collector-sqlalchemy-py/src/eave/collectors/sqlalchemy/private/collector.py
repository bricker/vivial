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
    is_user_table,
    save_identification_data,
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

                    self._save_user_identification_data(tablename, clauseelement, rparam)

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
                    pk_map_list = None
                    if isinstance(result, sqlalchemy.CursorResult) and len(result.inserted_primary_key_rows) > idx:
                        row = result.inserted_primary_key_rows[idx]
                        # sqlalchemy should put these in the same order in the case of composite pk
                        pk_names = [col.name for col in clauseelement.table.primary_key]
                        pk_values = [str(pk) for pk in row._tuple()]  # noqa: SLF001
                        pk_map_list = tuple(zip(pk_names, pk_values))

                    if pk_map_list:
                        # add pk values to rparam's column->value mapping
                        column_data = rparam.copy()
                        column_data.update(dict(pk_map_list))
                        save_identification_data(table_name=tablename, column_value_map=column_data)

                    rparam["__primary_keys"] = pk_map_list

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
                    self._save_user_identification_data(tablename, clauseelement, rparam)

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

    def _save_user_identification_data(
        self, tablename: str, clauseelement: sqlalchemy.Select | sqlalchemy.Update, params: dict[str, Any]
    ) -> None:
        """
        Preserves user/account table (suspected) primary and foreign key names + values
        to correlation context.

        Combines WHERE clause equivalence ('=') expression column->value mapping with
        remaining statment `params` which were not part of the WHERE clause (implying
        they should be part of an UPDATE statement column assignment, which may also
        contain data we are interested in persisting.)

        e.g. `UPDATE accounts SET team_id=:team_id, name=:name WHERE accounts.id = :accounts_id AND accounts.created < :last_week`
        should extract and save the mappings `{"id": "accounts_id_value", "team_id": "team_id_value"}`
        """
        if is_user_table(tablename):
            # construct statement_params from passed in and clause; SELECT statements
            # always has empty params and full clause.params, but UPDATE etc. always
            # has full params and empty clause.params. So we join them together here.
            compiled_clause = clauseelement.compile()
            statement_params = params.copy()
            non_none_clause_params = {k: v for k, v in dict(compiled_clause.params).items() if v is not None}
            statement_params.update(non_none_clause_params)

            where_clause = clauseelement.whereclause
            if where_clause is not None:
                # extract terms as list of binary expressions
                if isinstance(where_clause, sqlalchemy.BooleanClauseList):
                    where_clause = list(where_clause)
                else:
                    where_clause = [where_clause]

                # build col name -> value mapping from where clause expressions
                column_value_map = {}
                for expr in where_clause:
                    if not (
                        isinstance(expr, sqlalchemy.BinaryExpression)
                        and expr.operator == sqlalchemy.sql.operators.eq  # type: ignore
                        and isinstance(expr.left, sqlalchemy.Column)
                    ):
                        # we only care about binary expressions comparing if
                        # columns are equal to a value; otherwise we can't make assumptions
                        # about where clause values equating to the column value.
                        # TODO: delete values from statement_params for expr that doesn't match
                        continue

                    col_name = expr.left.name
                    # strip leading colon off param key (e.g. :id_1 -> id_1)
                    param_key = str(expr.right).lstrip(":")
                    param_value = statement_params.get(param_key, None)
                    field_table = expr.left.table.name
                    if param_value is not None and field_table == tablename:
                        column_value_map[col_name] = param_value

                    # delete where-clause param key from statement dict; we've
                    # now added the correct col name mapping to `column_value_map`,
                    # so we don't want to pollute it later with keys that aren't
                    # actual column names
                    del statement_params[param_key]

                # combine proper where-clause column->value mapping with
                # remaining value mappings from `statement_params`
                # (mostly to make sure UPDATE values get saved along w/
                # values from the WHERE filter)
                column_value_map.update(statement_params)
                save_identification_data(table_name=tablename, column_value_map=column_value_map)
