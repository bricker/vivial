#!/usr/bin/env python
import argparse
import asyncio
import os
import signal
import sys
from types import FrameType
from typing import LiteralString, cast

import psycopg
from eave.collectors.core.datastructures import EventType
from eave.collectors.core.write_queue import BatchWriteQueue, QueueParams
from psycopg import sql

# payload can only be 8kb max
# NEW variable documented here: https://www.postgresql.org/docs/current/plpgsql-trigger.html

_thisdir = os.path.dirname(__file__)
with open(os.path.join(_thisdir, "triggers.sql"), encoding="utf-8") as f:
    _TRIGGERS_SQL = sql.SQL(cast(LiteralString, f.read()))

# TODO: think about how this would work w/ a distributed db system w/ replication (becuse multiple db will get the same update cascaded.)
#    > maybe only needs to be running on the master replica


async def start_agent(conninfo: str, team_id: str) -> None:
    """
    listen and poll for notifications for a postgresql database (requires pg version 12+)

    To create or replace a trigger on a table, the user must have the TRIGGER privilege on the table. The user must also have EXECUTE privilege on the trigger function.
    https://www.postgresql.org/docs/current/sql-createtrigger.html
    """

    conn = await psycopg.AsyncConnection.connect(conninfo=conninfo, autocommit=True)

    def _sighandler(signum: int, frame: FrameType | None) -> None:
        sys.exit()

    signal.signal(signal.SIGINT, _sighandler)

    queue_params = QueueParams(event_type=EventType.dbchange, maxsize=100, maxage_seconds=30)
    q = BatchWriteQueue(queue_params=queue_params)

    try:
        async with conn.cursor() as curs:
            # **IMPORTANT**
            # LISTEN registers the _current_ session as a listener. Whenever NOTIFY is invoked, only the sessions _currently_ listening on that notification channel are notified
            await curs.execute(
                sql.SQL("\n").join(
                    [
                        _TRIGGERS_SQL,
                        sql.SQL("CALL eave_install_triggers();"),
                        sql.SQL("LISTEN eave_dbchange_channel;"),
                    ]
                )
            )

        print("Eave PostgreSQL agent started (Ctrl-C to stop)")
        q.start_autoflush()

        gen = conn.notifies()
        async for notify in gen:
            q.put(notify.payload)

    finally:
        q.stop_autoflush()
        await conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Eave Postgresql trace agent", description="Starts listening for database change events"
    )
    parser.add_argument("-d", "--database", help="name of the database to track changes in")
    parser.add_argument("-u", "--username", help="username to connect to db with")
    parser.add_argument("-p", "--password", help="user password to connect to db with")
    parser.add_argument("-t", "--team-id", help="eave team ID")

    args = parser.parse_args()

    asyncio.run(
        start_agent(
            conninfo="postgresql://eave-agent:dev@localhost:5433/eave-test",
            team_id=args.team_id,
        )
    )
