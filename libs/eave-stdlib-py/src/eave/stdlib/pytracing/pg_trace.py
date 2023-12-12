from datetime import datetime
import json
from uuid import uuid4
import time
import threading
import atexit
import multiprocessing
import psycopg2

from eave.stdlib.pytracing.datastructures import EventParams, EventType, RawEvent, PostgresDatabaseChangeEventParams
from .write_queue import BatchWriteQueue, write_queue

channel = "crud_events_channel"


# TODO: think about how this would work w/ a distributed db system w/ replication (becuse multiple db will get the same update cascaded.)
#    > maybe only needs to be running on the master replica
def start_postgresql_listener(db_name: str, user_name: str, user_password: str) -> None:
    """
    listen and poll for notifications for a postgresql database (requires pg version 12+)

    launches a background thread to listen for the events.

    To create or replace a trigger on a table, the user must have the TRIGGER privilege on the table. The user must also have EXECUTE privilege on the trigger function.
    https://www.postgresql.org/docs/current/sql-createtrigger.html

    """
    # NOTE: we could alternatively init connection w/ host/port instead of user/pas
    conn = psycopg2.connect(database=db_name, user=user_name, password=user_password)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    curs = conn.cursor()
    try:
        # create notify trigger
        trigger_fn_base = "crud_events_notifier"
        trigger_name_base = "crud_event"

        # reflection on pg db for all tables+events, so we can set listen/notify on all of them
        curs.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        # gotta unbox table name from single-value tuples :\
        table_names = map(lambda x: x[0], curs.fetchall())
        # https://www.postgresql.org/docs/current/sql-createtrigger.html
        action_names = ["UPDATE", "INSERT", "DELETE"]

        for table_name in table_names:
            for action_name in action_names:
                trigger_name = f"{trigger_name_base}_{action_name}_{table_name}"
                trigger_fn = f"{trigger_fn_base}_{action_name}_{table_name}"
                # print(f"creating {trigger_fn}\n")

                # TODO: using the sql builtin current_timestamp function may get us in trouble... sync w/ other events ts
                # payload can only be 8kb max
                # NEW variable documented here: https://www.postgresql.org/docs/current/plpgsql-trigger.html
                curs.execute(
                    f"""
CREATE OR REPLACE FUNCTION {trigger_fn}()
RETURNS TRIGGER AS $$
DECLARE
    v_txt text;
    data record;
BEGIN
    -- capture old row data if row is deleted, otherwise capture new row data
    IF TG_OP = 'DELETE' THEN
        data := OLD;
    ELSE
        data := NEW;
    END IF;

    v_txt := format('{{"table_name": "{table_name}", "operation": "%s", "operated_data": %s, "timestamp": "%s"}}', TG_OP, to_jsonb(data), current_timestamp);

    -- Notify the event writer when an update occurs
    PERFORM pg_notify('{channel}', v_txt);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER {trigger_name}
AFTER {action_name} ON {table_name}
FOR EACH ROW
EXECUTE PROCEDURE {trigger_fn}();
"""
                )
    finally:
        curs.close()
        conn.close()

    # launch worker process to poll for notify events
    write_queue.start_autoflush()

    # _poll_for_events(db_name, user_name, user_password)

    _process = multiprocessing.Process(
        target=_poll_for_events,
        kwargs={
            "db_name": db_name,
            "user_name": user_name,
            "user_password": user_password,
            # "write_queue": write_queue,
        },
    )

    def kill_event_process() -> None:
        write_queue.stop_autoflush()
        _process.terminate()

    atexit.register(kill_event_process)
    _process.start()

    # bg_thread = threading.Thread(target=_poll_for_events, args=(db_name, user_name, user_password))
    # bg_thread.daemon = True
    # bg_thread.start()


def _poll_for_events(
    db_name: str,
    user_name: str,
    user_password: str,
    # write_queue: BatchWriteQueue,
) -> None:
    # TODO: does psycopg2 have thread safe connection acces????
    # TODO: is possible recreate connection? dont think so; not w/o possibly missing events. keeping 1 connection open indefinitely not great tho
    conn = psycopg2.connect(database=db_name, user=user_name, password=user_password)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    # **IMPORTANT**
    # LISTEN registers the _current_ session as a listener. Whenever NOTIFY is invoked, only the sessions _currently_ listening on that notification channel are notified
    with conn.cursor() as curs:
        curs.execute(f"LISTEN {channel};")

    try:
        while True:
            # chill
            time.sleep(5)

            # gotta poll db conn for any updates?
            conn.poll()

            while conn.notifies:
                notify = conn.notifies.pop(0)
                print(f"send to clickhosue: {notify.payload}")
                json_data = json.loads(notify.payload)
                write_queue.put(
                    event=RawEvent(
                        team_id=uuid4(),  # TODO: this is still junk. not sure how to get this data yet
                        corr_id=uuid4(),
                        timestamp=datetime.fromisoformat(json_data["timestamp"]),
                        event_type=EventType.dbchange,
                        event_params=PostgresDatabaseChangeEventParams(
                            table_name=json_data["table_name"],
                            operation=json_data["operation"],
                            operated_data=json.dumps(json_data["operated_data"]),
                        ),
                    )
                )
    finally:
        conn.close()
