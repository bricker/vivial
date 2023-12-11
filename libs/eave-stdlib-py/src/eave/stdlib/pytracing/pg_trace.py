from datetime import datetime
from uuid import uuid4
import time
import threading
import psycopg2

from eave.stdlib.pytracing.datastructures import EventParams, EventType, RawEvent, PostgresDatabaseChangeEventParams
from .write_queue import write_queue

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
                # TODO: what better data can we pass in our plpgsql function payload??? structure as JSON to parse later??
                # payload can only be 8kb max
                # EXECUTE
                #  format(
                #     'NOTIFY tab, %L',
                #     to_char(NEW.ts, 'YYYY-MM-DD')
                #  );
                curs.execute(
                    f"""
CREATE OR REPLACE FUNCTION {trigger_fn}()
RETURNS TRIGGER AS $$
DECLARE
    v_txt text;
BEGIN
    v_txt := format('something happened: {action_name} on {table_name}. sending message for %s, %s', TG_OP, NEW);
    RAISE NOTICE '%', v_txt;
    -- Notify the external application when an update occurs
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

    # launch worker thread to poll for notify events
    write_queue.start_autoflush()
    bg_thread = threading.Thread(target=_poll_for_events, args=(db_name, user_name, user_password))
    bg_thread.daemon = True
    bg_thread.start()


def _poll_for_events(db_name: str, user_name: str, user_password: str) -> None:
    # TODO: does psycopg2 have thread safe connection acces????
    # TODO: is possible recreate connection? keeping 1 connection open indefinitely not great
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
                print("Notification:", notify.payload)
                write_queue.put(
                    event=RawEvent(
                        team_id=uuid4(),
                        corr_id=uuid4(),
                        timestamp=datetime.now(),  # TODO this should be date at db write time, not event ack time. can it be gotten in notify function?
                        event_type=EventType.dbchange,
                        event_params=PostgresDatabaseChangeEventParams(
                            payload=notify.payload,
                        ),
                    )
                )
    finally:
        conn.close()
