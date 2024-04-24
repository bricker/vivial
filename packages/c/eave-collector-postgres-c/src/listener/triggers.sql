CREATE OR REPLACE FUNCTION eave_notify_dbchange()
RETURNS TRIGGER
AS $$
DECLARE
    channel_name VARCHAR := 'eave_dbchange_channel';
    ts INTEGER := TRUNC(EXTRACT(EPOCH FROM CURRENT_TIMESTAMP));
BEGIN
    -- pg_notify payload can only be 8kb max (under default db config)
    -- (i am unsure about behavior if it is given more than 8kb)
    -- https://www.postgresql.org/docs/current/sql-notify.html
    IF (TG_OP = 'INSERT') THEN
        PERFORM pg_notify(channel_name,
            '{"table_name":"' || TG_TABLE_NAME ||
            '","operation":"' || TG_OP ||
            '","new_data":' || row_to_json(NEW, FALSE) ||
            ',"old_data":null,"timestamp":"' || ts || '"}'
        );

    ELSIF (TG_OP = 'UPDATE') THEN
        PERFORM pg_notify(channel_name,
            '{"table_name":"' || TG_TABLE_NAME ||
            '","operation":"' || TG_OP ||
            '","new_data":' || row_to_json(NEW, FALSE) ||
            ',"old_data":' || row_to_json(OLD, FALSE) ||
            ',"timestamp":"' || ts || '"}'
        );

    ELSIF (TG_OP = 'DELETE') THEN
        PERFORM pg_notify(channel_name,
            '{"table_name":"' || TG_TABLE_NAME ||
            '","operation":"' || TG_OP ||
            '","new_data":null,"old_data":' || row_to_json(OLD, FALSE) ||
            ',"timestamp":"' || ts || '"}'
        );
    END IF;

    -- return NEW to avoid potential errors from other triggers:
    -- "[return value of] AFTER is always ignored; it might as well be null. However,
    -- any of these types of triggers might still abort the entire operation by raising an error."
    -- https://www.postgresql.org/docs/current/plpgsql-trigger.html
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE eave_install_triggers()
AS $$
DECLARE
    t RECORD;
    trigname VARCHAR := 'eave_dbchange_trigger';
BEGIN
    FOR t IN
        SELECT DISTINCT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    LOOP
        PERFORM 1 FROM information_schema.triggers
        WHERE event_object_table = t.table_name
        AND trigger_name = trigname;

        IF NOT FOUND THEN
            EXECUTE CONCAT_WS(' ',
                'CREATE CONSTRAINT TRIGGER', trigname,
                'AFTER INSERT OR UPDATE OR DELETE',
                'ON', quote_ident(t.table_name),
                'DEFERRABLE INITIALLY DEFERRED',
                'FOR EACH ROW',
                'EXECUTE PROCEDURE eave_notify_dbchange()'
            );
        END IF;
    END LOOP;
END;
-- This file must end with a ';', so that listener.c appended commands work as expected
$$ LANGUAGE plpgsql;
