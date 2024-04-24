import os
import re
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any, Self

import asyncpg
import asyncpg.prepared_stmt

from eave.collectors.core.wrap_util import wrap, wrap_async

_thisdir = os.path.dirname(__file__)
with open(os.path.join(_thisdir, "triggers.sql"), encoding="utf-8") as f:
    _TRIGGERS_SQL = f.read()

_prepared_statement_funcs = [
    asyncpg.prepared_stmt.PreparedStatement.executemany,
    asyncpg.prepared_stmt.PreparedStatement.fetch,
    asyncpg.prepared_stmt.PreparedStatement.fetchval,
    asyncpg.prepared_stmt.PreparedStatement.fetchrow,
]

_connection_funcs = [
    asyncpg.connection.Connection.execute,
    asyncpg.connection.Connection.executemany,
    asyncpg.connection.Connection.fetch,
    asyncpg.connection.Connection.fetchval,
    asyncpg.connection.Connection.fetchrow,
]


@dataclass
class _TableColumn:
    column_name: str
    data_type: str
    ordinal_position: int


@dataclass
class _TableSchema:
    columns: list[_TableColumn]

    @classmethod
    def from_records(cls, records: list[asyncpg.Record]) -> Self:
        return cls(
            columns=[
                _TableColumn(
                    column_name=record.column_name, data_type=record.data_type, ordinal_position=record.ordinal_position
                )
                for record in records
            ]
        )


class AsyncpgCollector:
    _connect_args: tuple[Any]
    _connect_kwargs: dict[str, Any]
    _connection: asyncpg.Connection | None
    _enabled: bool
    _schema_cache: dict[str, _TableSchema]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # TODO: The args and kwargs are pass-through to asyncpg.connect(). They need some kind of documentation.
        self._connect_args = args
        self._connect_kwargs = kwargs
        self._connection = None
        self._enabled = False
        self._schema_cache = {}

    async def start(self) -> None:
        connection: asyncpg.Connection = await asyncpg.connect(*self._connect_args, **self._connect_kwargs)
        await connection.execute(
            "\n".join(
                [
                    _TRIGGERS_SQL,
                    "CALL eave_install_triggers();",
                ]
            )
        )
        await connection.add_listener(channel="eave_dbchange_channel", callback=self._pg_notification_listener)
        self._install_wrappers()
        self._connection = connection
        self._enabled = True

    async def stop(self) -> None:
        self._enabled = False
        if self._connection:
            await self._connection.close()
            # When connections are closed, listeners are discarded, so explicitly removing a listener is unnecessary.

        self._connection = None

    def _install_wrappers(self) -> None:
        for func in _connection_funcs:
            wrap(
                module=func.__module__,
                name=func.__qualname__,
                wrapper=self._eave_wrapper__asyncpg_connection_Connection_default,
                check_enabled=self._check_enabled,
            )

        for func in _prepared_statement_funcs:
            wrap_async(
                module=func.__module__,
                name=func.__qualname__,
                wrapper=self._eave_wrapper__asyncpg_prepared_stmt_PreparedStatement_default,
                check_enabled=self._check_enabled,
            )

    def _eave_wrapper__asyncpg_connection_Connection_default[T, **P](  # noqa: N802
        self,
        wrapped: Callable[P, T],
        instance: asyncpg.connection.Connection,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> T:
        # print(wrapped, args, kwargs)
        # normalizedargs = normalized_args(wrapped, args, kwargs)
        # pprint.pprint(normalizedargs)
        return wrapped(*args, **kwargs)

    async def _eave_wrapper__asyncpg_prepared_stmt_PreparedStatement_default[T, **P](  # noqa: N802
        self,
        wrapped: Callable[P, Coroutine[Any, Any, T]],
        instance: asyncpg.prepared_stmt.PreparedStatement,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> T:
        # if m := re.match((r"select\s+.+?\sfrom\s+" + tablematcher + r"[\s;]"), q, re.IGNORECASE | re.MULTILINE):
        #     tablename = m.group(1)
        # elif m := re.match((r"insert\s+into\s+" + tablematcher + r"\s"), q, re.IGNORECASE | re.MULTILINE):
        #     tablename = m.group(1)
        # elif m := re.match((r"update\s+" + tablematcher + r"\s"), q, re.IGNORECASE | re.MULTILINE):
        #     tablename = m.group(1)
        # elif m := re.match((r"delete from\s+" + tablematcher + r"[\s;]"), q, re.IGNORECASE | re.MULTILINE):
        #     tablename = m.group(1)
        # else:
        #     EAVE_LOGGER.warning("table name couldn't be determined.")
        #     tablename = None

        # if tablename and self._connection is not None:
        #     print(tablename)

        #     if not self._schema_cache[tablename]:
        #         r = await self._connection.fetch(dedent(
        #         """
        #             SELECT column_name, data_type, ordinal_position
        #             FROM information_schema.columns
        #             WHERE table_schema = $1
        #                 AND table_name = $2
        #             ORDER BY ordinal_position;
        #             """), "public", tablename)
        #         self._schema_cache[tablename] = _TableSchema.from_records(r)

        # normalizedargs = normalized_args(wrapped, args, kwargs)
        # pprint.pprint(normalizedargs)
        r = await wrapped(*args, **kwargs)

        q = instance.get_query()
        # print("attributes", instance.get_attributes())
        # print("parameters", instance.get_parameters())
        tablematcher = r"[`\"']?([a-zA-Z0-9_\.\-]+)[`\"']?"

        if m := re.match((r"select\s+.+?\sfrom\s+" + tablematcher + r"[\s;]"), q, re.IGNORECASE | re.MULTILINE):
            print("Logging SELECT...", q)
            tablename = m.group(1)
            print("tablename=", tablename)
            print("args", args)
            print("kwargs", kwargs)
            print("attributes", instance.get_attributes())
            print("parameters", instance.get_parameters())

        return r

    async def _pg_notification_listener(
        self, connection: asyncpg.Connection, pid: str, channel: str, payload: Any
    ) -> None:
        print(">>> received pg notification", connection, pid, channel, payload)
        print()

    def _check_enabled(self) -> bool:
        return self._enabled
