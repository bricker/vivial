import re
import time
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any

from django.db.backends.utils import CursorWrapper

from eave.collectors.core.base_collector import BaseCollector
from eave.collectors.core.correlation_context import corr_ctx
from eave.collectors.core.datastructures import DatabaseEventPayload, DatabaseOperation, DatabaseStructure
from eave.collectors.core.write_queue import WriteQueue


class EaveCursorWrapper(CursorWrapper):
    # altered from django.db.backends.utils.CursorDebugWrapper

    _leading_comment_remover = re.compile(r"^/\*.*?\*/")
    _white_space_reducer = re.compile(r"\s+")

    def __init__(self, write_queue: WriteQueue, cursor: Any, db: Any) -> None:
        super().__init__(cursor, db)
        self.write_queue = write_queue

    def execute(self, sql, params=None) -> None:
        with self.capture_sql(sql, params, use_last_executed_query=True):
            return super().execute(sql, params)

    def executemany(self, sql, param_list) -> None:
        with self.capture_sql(sql, param_list, many=True):
            return super().executemany(sql, param_list)

    @contextmanager
    def capture_sql(self, sql=None, params=None, use_last_executed_query=False, many=False):
        # start = time.monotonic()
        try:
            # yield execution to wrapped context
            yield
        finally:
            # stop = time.monotonic()
            # duration = stop - start
            if use_last_executed_query:
                sql = self.db.ops.last_executed_query(self.cursor, sql, params)
            # try:
            #     times = len(params) if many else ""
            # except TypeError:
            #     # params could be an iterator.
            #     times = "?"

            if sql is not None:
                sql = self._leading_comment_remover.sub("", sql)
                sql = self._white_space_reducer.sub(" ", sql)

                op = self._get_operation_name(sql)
                table_name = self._get_table_name(sql, op)

                record = DatabaseEventPayload(
                    timestamp=time.time(),
                    db_structure=DatabaseStructure.SQL,
                    operation=op,
                    db_name=self.db.alias,
                    statement=sql,
                    table_name=table_name,
                    parameters=params,  # TODO: params is usually None; django doesnt remove param values from the statement
                    context=corr_ctx.to_dict(),
                )

                self.write_queue.put(record)
            # print(
            #     {
            #         "sql": "%s times: %s" % (times, sql) if many else sql,
            #         "time": "%.3f" % duration,
            #     }
            # )

    def _get_operation_name(self, sql: str) -> DatabaseOperation:
        op_str = sql.split()[0]
        return DatabaseOperation.from_str(op_str) or DatabaseOperation.UNKNOWN

    def _get_table_name(self, sql: str, op: DatabaseOperation) -> str:
        unknown = "__unknown"  # TODO: placeholder?
        parts = sql.split()

        match op:
            case DatabaseOperation.SELECT:
                for i, part in enumerate(parts):
                    if part.upper() == "FROM" and len(parts) > i + 1:
                        return parts[i + 1]
            case DatabaseOperation.INSERT | DatabaseOperation.DELETE:
                if len(parts) >= 3:
                    return parts[2]
            case DatabaseOperation.UPDATE:
                if len(parts) >= 2:
                    return parts[1]
        return unknown


class DjangoOrmCollector(BaseCollector):
    def _eave_cursor_factory(self) -> Callable[[Any, Any], EaveCursorWrapper]:
        def cursor_creator(db: Any, cursor: Any) -> EaveCursorWrapper:
            return EaveCursorWrapper(self.write_queue, cursor, db)

        return cursor_creator

    def instrument(self) -> None:
        from django.db.backends.base.base import BaseDatabaseWrapper

        if getattr(BaseDatabaseWrapper, "_is_instrumented_by_eave", False):
            return

        # Save the original method for uninstrumenting
        self._original_make_debug_cursor = BaseDatabaseWrapper.make_debug_cursor  # type: ignore

        # monkey patch
        BaseDatabaseWrapper.make_debug_cursor = self._eave_cursor_factory()  # type: ignore

        BaseDatabaseWrapper._is_instrumented_by_eave = True  # type: ignore

    def uninstrument(self) -> None:
        from django.db.backends.base.base import BaseDatabaseWrapper

        if not getattr(BaseDatabaseWrapper, "_is_instrumented_by_eave", False):
            return

        # reset original method
        BaseDatabaseWrapper.make_debug_cursor = self._original_make_debug_cursor  # type: ignore

        BaseDatabaseWrapper._is_instrumented_by_eave = False  # type: ignore
