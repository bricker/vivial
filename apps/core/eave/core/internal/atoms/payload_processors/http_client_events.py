from typing import Any

from eave.stdlib.logging import LogContext

from ..table_handle import BigQueryTableHandle


class HttpClientEventsTableHandle(BigQueryTableHandle):
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

        # formatted_rows: list[dict[str, Any]] = []

        # for e in http_client_events:
        #     if e.request_method is None or e.request_url is None:
        #         LOGGER.warning("e.request_method or e.request_url unexpectedly missing", ctx)
        #         continue

        #     row = e.to_dict()
        #     formatted_rows.append(row)

        # errors = self._bq_client.append_rows(
        #     table=remote_table,
        #     rows=formatted_rows,
        # )

        # if len(errors) > 0:
        #     LOGGER.warning("BigQuery insert errors", {"errors": cast(list, errors)}, ctx)
