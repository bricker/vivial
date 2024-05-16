from typing import Any, Callable
import time
from contextlib import contextmanager

from django.db.models import Model
from django.db.models import signals
from django.db import connection
from django.db.backends.utils import CursorWrapper, CursorDebugWrapper
from eave.collectors.core.write_queue import WriteQueue


class EaveCursorWrapper(CursorWrapper):
    # altered from django.db.backends.utils.CursorDebugWrapper

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
        start = time.monotonic()
        try:
            # yield execution to wrapped context
            yield
        finally:
            stop = time.monotonic()
            duration = stop - start
            # if use_last_executed_query:
            #     sql = self.db.ops.last_executed_query(self.cursor, sql, params)
            try:
                times = len(params) if many else ""
            except TypeError:
                # params could be an iterator.
                times = "?"

            # TODO: write queue
            # self.db.queries_log.append(
            print(
                {
                    "sql": "%s times: %s" % (times, sql) if many else sql,
                    "time": "%.3f" % duration,
                }
            )
            # logger.debug(
            #     "(%.3f) %s; args=%s; alias=%s",
            #     duration,
            #     sql,
            #     params,
            #     self.db.alias,
            #     extra={
            #         "duration": duration,
            #         "sql": sql,
            #         "params": params,
            #         "alias": self.db.alias,
            #     },
            # )


# """
# use signal pre_save and post_save events to clear and read queries?
# PROBLEMS:
# - this feature only works in debug mode
# - query log reading probs istn thread-safe: query log may have accumulated more qureies (or been deleted again) by time post_save is executed

# # Clear any previously stored queries
# connection.queries_log.clear()

# # Perform the save operation
# obj = MyModel(field1='value1', field2='value2')
# obj.save()

# # Print the SQL queries
# for query in connection.queries:
#     print(query['sql'])
# """

"""
MONKEY PATHC:

find the db wrapper instance... > connection.force_debug_cursor
connection.force_debug_cursor = True
( do we have to set this before db is init? or will it fetch updated ref for every statment?)

connection.make_debug_cursor = return custom class similar to CursorDebugWrapper except it writes to queue
"""

from eave.collectors.core.base_collector import BaseCollector
from eave.collectors.core.datastructures import DatabaseStructure, DatabaseOperation
from eave.collectors.core.correlation_context import corr_ctx

"""
setup hast o be calle dbefore we can access any orm models (do we need to??)
> django.setup()

check settings to see if django has been setup yet (django.conf.settings[.configured])


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
"""


class DjangoOrmCollector(BaseCollector):
    def _pre_model_saved(
        self, sender: type, instance: Model, raw: bool, using: str, update_fields: Any | None, *args, **kwargs
    ):
        # Clear any previously stored queries
        connection.queries_log.clear()
        print(connection.make_debug_cursor)

    def _post_model_saved(
        self,
        sender: type,
        instance: Model,
        created: bool,
        raw: bool,
        using: str,
        update_fields: Any | None,
        *args,
        **kwargs,
    ) -> None:
        """
        https://docs.djangoproject.com/en/5.0/ref/signals/#post-save
        """
        # TODO: write to writequeue
        print("model got saved:", sender, instance, created, raw, using, update_fields)
        # model got saved: <class 'polls.models.Question'> "did orm tracking work?" True False "default" None
        for query in connection.queries:
            # { sql: "statemnt", time: duration }
            print(query["sql"])
            # UPDATE "polls_choice" SET "question_id" = 1, "choice_text" = 'Not much', "votes" = ("polls_choice"."votes" + 1) WHERE "polls_choice"."id" = 1

    def _eave_cursor_factory(self) -> Callable[[Any, Any], EaveCursorWrapper]:
        def cursor_creator(db: Any, cursor: Any) -> EaveCursorWrapper:
            return EaveCursorWrapper(self.write_queue, cursor, db)

        return cursor_creator

    def instrument(self) -> None:
        # track create/update events
        # signals.post_save.connect(self._post_model_saved)
        # signals.pre_save.connect(self._pre_model_saved)

        # connection.make_debug_cursor = self._eave_cursor_factory()
        # connection.force_debug_cursor = True
        # we should only need to override the normal function in prod, but make_debug_cursor is used in django DEBUG mode
        # connection.make_cursor = self._eave_cursor_factory()

        from django.db.backends.base.base import BaseDatabaseWrapper

        if getattr(BaseDatabaseWrapper, "_is_instrumented_by_eave", False):
            return

        BaseDatabaseWrapper._is_instrumented_by_eave = True

        # Save the original method so you can still call it if needed
        BaseDatabaseWrapper._original_make_debug_cursor = BaseDatabaseWrapper.make_debug_cursor

        # monkey patch
        BaseDatabaseWrapper.make_debug_cursor = self._eave_cursor_factory() # type: ignore


    def uninstrument(self) -> None:
        """dont need to call this if `Signal.connect` was called with `weak=True` kwarg (the default value)"""
        signals.post_save.disconnect(self._post_model_saved)
