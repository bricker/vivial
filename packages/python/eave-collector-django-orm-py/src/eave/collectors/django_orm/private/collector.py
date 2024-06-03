import re
import time
from collections.abc import Callable, Generator, Mapping, Sequence
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.utils import CursorWrapper

from eave.collectors.core.base_collector import BaseCollector
from eave.collectors.core.correlation_context import corr_ctx
from eave.collectors.core.datastructures import DatabaseEventPayload, DatabaseOperation, DatabaseStructure
from eave.collectors.core.write_queue import WriteQueue

# Copied from Django
_Mixed = None | bool | int | float | Decimal | str | bytes | datetime | UUID
_SQLType = _Mixed | Sequence[_Mixed] | Mapping[str, _Mixed]
_ParamsType = Sequence[_SQLType] | Mapping[str, _SQLType]


class EaveCursorWrapper(CursorWrapper):
    # altered from django.db.backends.utils.CursorDebugWrapper

    _leading_comment_remover = re.compile(r"^/\*.*?\*/")
    _white_space_reducer = re.compile(r"\s+")

    def __init__(self, write_queue: WriteQueue, cursor: Any, db: Any) -> None:
        super().__init__(cursor, db)
        self.write_queue = write_queue

    def execute(self, sql: str, params: _ParamsType | None = None) -> None:
        with self.capture_sql(sql=sql, params=params, use_last_executed_query=True):
            return super().execute(sql, params)

    def executemany(self, sql: str, param_list: Sequence[_ParamsType | None]) -> None:
        with self.capture_sql(sql=sql, multiparams=param_list, many=True):
            return super().executemany(sql, param_list)

    @contextmanager
    def capture_sql(
        self,
        *,
        sql: str | None = None,
        params: _ParamsType | None = None,
        multiparams: Sequence[_ParamsType | None] | None = None,
        use_last_executed_query: bool = False,
        many: bool = True,
    ) -> Generator[None, Any, None]:
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

                # FIXME: Resolve params vs. multiparams
                # rparams: _ParamsType | None = None
                # if params:
                #     rparams = params
                # elif multiparams and len(multiparams) > 0:
                #     rparams = multiparams[0]

                record = DatabaseEventPayload(
                    timestamp=time.time(),
                    operation=op,
                    db_name=self.db.alias,
                    statement=sql,
                    table_name=table_name,
                    parameters=None,  # TODO: params is usually None; django doesnt remove param values from the statement
                )

                self.write_queue.put(record)

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
        if getattr(BaseDatabaseWrapper, "_is_instrumented_by_eave", False):
            return

        # Save the original method for uninstrumenting
        self._original_make_debug_cursor = BaseDatabaseWrapper.make_debug_cursor  # type: ignore

        # monkey patch
        BaseDatabaseWrapper.make_debug_cursor = self._eave_cursor_factory()  # type: ignore

        BaseDatabaseWrapper._is_instrumented_by_eave = True  # type: ignore  # noqa: SLF001

    def uninstrument(self) -> None:
        if not getattr(BaseDatabaseWrapper, "_is_instrumented_by_eave", False):
            return

        # reset original method
        BaseDatabaseWrapper.make_debug_cursor = self._original_make_debug_cursor  # type: ignore

        BaseDatabaseWrapper._is_instrumented_by_eave = False  # type: ignore  # noqa: SLF001
