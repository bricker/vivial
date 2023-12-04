import clickhouse_connect

chclient = clickhouse_connect.get_client(host='localhost')

chclient.command(cmd="drop table raw_events")

chclient.command(
    cmd=" ".join([
        "create table if not exists raw_events (",
            "team_id UUID,",
            "timestamp DateTime64(6),",
            "event_type LowCardinality(String),",
            "event_params JSON",
        ")",
        "engine MergeTree",
        "primary key (team_id, timestamp)",
    ]),
    settings={
        "allow_experimental_object_type": 1,
    },
)