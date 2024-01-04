import clickhouse_connect

chclient = clickhouse_connect.get_client(host="localhost")

chclient.command(cmd="drop table if exists raw_events")

chclient.command(cmd="drop table if exists dev_db_ops")
chclient.command(
    cmd=" ".join(
        [
            "create table if not exists dev_dbchanges (",
            "timestamp DateTime64(6, 'UTC'),",
            "table_name String,",
            "operation Enum('insert', 'update', 'delete'),"
            "old_data JSON",
            "new_data JSON ",
            ")",
            "engine MergeTree",
            "primary key (team_id, timestamp)",
        ]
    ),
    settings={
        "allow_experimental_object_type": 1,
    },
)

# chclient.command(cmd="drop table if exists dev_functioncalls")
# chclient.command(
#     cmd=" ".join(
#         [
#             "create table if not exists dev_func_traces (",
#             "timestamp DateTime64(6, 'UTC'),",
#             "name String",
#             "params JSON",
#             "return_value_int Int64",
#             "return_value_str String",
#             ")",
#             "engine MergeTree",
#             "primary key (team_id, timestamp)",
#         ]
#     ),
#     settings={
#         "allow_experimental_object_type": 1,
#     },
# )

# chclient.command(cmd="drop table if exists dev_networkout")
# chclient.command(
#     cmd=" ".join(
#         [
#             "create table if not exists dev_outgoing_network_ops (",
#             "timestamp DateTime64(6),",
#             "method LowCardinality(String),",
#             "url String,",
#             "payload JSON,",
#             ")",
#             "engine MergeTree",
#             "primary key (team_id, timestamp)",
#         ]
#     ),
#     settings={
#         "allow_experimental_object_type": 1,
#     },
# )

# chclient.command(
#     cmd=" ".join(
#         [
#             "create table if not exists dev_incoming_network_ops (",
#             "timestamp DateTime64(6),",
#             "event_type LowCardinality(String),",
#             "event_params JSON",
#             ")",
#             "engine MergeTree",
#             "primary key (team_id, timestamp)",
#         ]
#     ),
#     settings={
#         "allow_experimental_object_type": 1,
#     },
# )
