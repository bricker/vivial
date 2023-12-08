from datetime import datetime
from uuid import uuid4
import time
import threading
import psycopg2

from eave.stdlib.pytracing.datastructures import EventParams, EventType, RawEvent, PostgresDatabaseChangeEventParams
from .write_queue import write_queue

def start_postgresql_listener(db_name: str, user_name: str, user_password: str) -> None:
    """
    listen and poll for notifications for a postgresql database (requires pg version 12+)

    launches a background thread to listen for the events.
    """
    # we could alternatively take host/port instead of user/pas
    conn = psycopg2.connect(database=db_name, user=user_name, password=user_password)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    # create listener
    channel = "crud_events_channel"
    curs = conn.cursor()
    curs.execute(f"LISTEN {channel};")

    # create notify trigger
    trigger_fn = "crud_events_notifier"
    trigger_name = "crud_event"

    # reflection on pg db for all tables+events, so we can set listen/notify on all of them
    curs.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    table_names = curs.fetchall()
    # https://www.postgresql.org/docs/current/sql-createtrigger.html
    action_names = ["UPDATE", "INSERT", "DELETE", "TRUNCATE"]
    
    for table_name in table_names:
        for action_name in action_names:
            # TODO: what better data can we pass in our plpgsql function payload??? structure as JSON to parse later??
            curs.execute(f"""
CREATE OR REPLACE FUNCTION {trigger_fn}()
RETURNS TRIGGER AS $$
BEGIN
    -- Notify the external application when an update occurs
    PERFORM pg_notify('{channel}', 'something happened: {action_name} on {table_name}');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER {trigger_name}
AFTER {action_name} ON {table_name}
FOR EACH ROW
EXECUTE FUNCTION {trigger_fn}();
""")
    
    # launch worker thread to poll for notify events
    bg_thread = threading.Thread(target=_poll_for_events, args=(db_name, user_name, user_password))
    bg_thread.daemon = True
    bg_thread.start()
    

def _poll_for_events(db_name: str, user_name: str, user_password: str) -> None:
    while True:
        # chill
        time.sleep(5)

        # recreate connection; keeping 1 connection open indefinitely not great
        conn = psycopg2.connect(database=db_name, user=user_name, password=user_password)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        if conn.poll():
            while conn.notifies:
                notify = conn.notifies.pop(0)
                print("Notification:", notify.payload)
                write_queue.put(event=RawEvent(
                    team_id=uuid4(),
                    corr_id=uuid4(),
                    timestamp=datetime.now(), # TODO this should be date at db write time, not event ack time. can it be gotten in notify function?
                    event_type=EventType.dbchange,
                    event_params=PostgresDatabaseChangeEventParams(
                        payload=notify.payload,
                    )
                ))
