CREATE OR REPLACE FUNCTION eave_notify_dbchange()
RETURNS TRIGGER
AS $$
DECLARE
    channel_name VARCHAR := 'eave_dbchange_channel';
    ts INTEGER := TRUNC(EXTRACT(EPOCH FROM CURRENT_TIMESTAMP));
BEGIN
    IF (TG_OP = 'INSERT') THEN
        PERFORM pg_notify(channel_name,
            '{"table_name":"' || TG_TABLE_NAME ||
            '","operation":"' || TG_OP ||
            '","new_data":' || row_to_json(NEW, FALSE) ||
            ',"old_data":null,"timestamp":"' || ts || '"}'
        );
        RETURN NULL;

    ELSIF (TG_OP = 'UPDATE') THEN
        PERFORM pg_notify(channel_name,
            '{"table_name":"' || TG_TABLE_NAME ||
            '","operation":"' || TG_OP ||
            '","new_data":' || row_to_json(NEW, FALSE) ||
            ',"old_data":' || row_to_json(OLD, FALSE) ||
            ',"timestamp":"' || ts || '"}'
        );
        RETURN NULL;

    ELSIF (TG_OP = 'DELETE') THEN
        PERFORM pg_notify(channel_name,
            '{"table_name":"' || TG_TABLE_NAME ||
            '","operation":"' || TG_OP ||
            '","new_data":null,"old_data":' || row_to_json(OLD, FALSE) ||
            ',"timestamp":"' || ts || '"}'
        );
        RETURN NULL;
    END IF;
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
$$ LANGUAGE plpgsql;
