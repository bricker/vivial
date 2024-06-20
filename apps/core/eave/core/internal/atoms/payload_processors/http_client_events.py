from typing import Any

from eave.stdlib.logging import LogContext

from ..table_handle import BigQueryTableHandle


class HttpClientEventsTableHandle(BigQueryTableHandle):
    async def create_vevent_view(self, *, request_method: str, request_url: str) -> None:
        pass
        # vevent_readable_name = make_virtual_event_readable_name(operation=operation, table_name=source_table)
        # vevent_view_id = tableize(vevent_readable_name)

        # async with database.async_session.begin() as db_session:
        #     vevent_query = await VirtualEventOrm.query(
        #         session=db_session,
        #         params=VirtualEventOrm.QueryParams(
        #             team_id=self.team.id,
        #             view_id=vevent_view_id,
        #         ),
        #     )

        #     if not vevent_query.one_or_none():
        #         self._bq_client.get_or_create_view(
        #             dataset_id=self.dataset_id,
        #             view_id=vevent_view_id,
        #             view_query=dedent(
        #                 """
        #                 SELECT
        #                     *
        #                 FROM
        #                     {dataset_id}.{atom_table_id}
        #                 WHERE
        #                     `table_name` = {source_table}
        #                     AND `operation` = {operation}
        #                 ORDER BY
        #                     `timestamp` ASC
        #                 """.format(
        #                     dataset_id=sql_sanitized_identifier(self.dataset_id),
        #                     atom_table_id=sql_sanitized_identifier(self.table_def.table_id),
        #                     source_table=sql_sanitized_literal(source_table),
        #                     operation=sql_sanitized_literal(operation),
        #                 )
        #             ).strip(),
        #         )

        #         await VirtualEventOrm.create(
        #             session=db_session,
        #             team_id=self.team.id,
        #             view_id=vevent_view_id,
        #             readable_name=vevent_readable_name,
        #             description=f"{operation} operation on the {source_table} table.",
        #         )

    async def insert(self, events: list[dict[str, Any]], ctx: LogContext) -> None:
        pass
        # if len(events) == 0:
        #     return

        # http_client_events = [HttpClientEventPayload(**e) for e in events]

        # self._bq_client.get_or_create_dataset(dataset_id=self.dataset_id)

        # remote_table = self._bq_client.get_and_sync_or_create_table(
        #     table=self.construct_bq_table(),
        #     ctx=ctx,
        # )

        # unique_operations: set[tuple[str, str]] = set()
        # formatted_rows: list[dict[str, Any]] = []

        # for e in http_client_events:
        #     if e.request_method is None or e.request_url is None:
        #         LOGGER.warning("e.request_method or e.request_url unexpectedly missing", ctx)
        #         continue

        #     unique_operations.add((e.request_method, e.request_url))
        #     row = e.to_dict()
        #     formatted_rows.append(row)

        # errors = self._bq_client.append_rows(
        #     table=remote_table,
        #     rows=formatted_rows,
        # )

        # if len(errors) > 0:
        #     LOGGER.warning("BigQuery insert errors", {"errors": cast(list, errors)}, ctx)

        # # FIXME: This is vulnerable to a DoS
        # for request_method, request_url in unique_operations:
        #     await self.create_vevent_view(request_method=request_method, request_url=request_url)
