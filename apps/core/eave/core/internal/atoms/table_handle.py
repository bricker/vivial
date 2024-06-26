from google.cloud.bigquery import Table

from eave.core.internal import database
from eave.core.internal.atoms.atom_types import BigQueryTableDefinition
from eave.core.internal.atoms.db_views import BigQueryView
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm
from eave.core.internal.orm.team import bq_dataset_id
from eave.core.internal.orm.virtual_event import VirtualEventOrm
from eave.stdlib.logging import LOGGER, LogContext

from ..lib import bq_client


class BigQueryTableHandle:
    table_def: BigQueryTableDefinition
    _dataset_id: str
    _client: ClientCredentialsOrm

    def __init__(self, *, client: ClientCredentialsOrm) -> None:
        self._client = client
        self._dataset_id = bq_dataset_id(client.team_id)

    def get_or_create_table(self, *, ctx: LogContext) -> Table:
        # Lazily creates the dataset in case it doesn't exist.
        bq_client.EAVE_INTERNAL_BIGQUERY_CLIENT.get_or_create_dataset(dataset_id=self._dataset_id)

        table = bq_client.EAVE_INTERNAL_BIGQUERY_CLIENT.construct_table(
            dataset_id=self._dataset_id, table_id=self.table_def.table_id
        )
        table.description = self.table_def.description
        table.friendly_name = self.table_def.friendly_name
        table.schema = self.table_def.schema

        table = bq_client.EAVE_INTERNAL_BIGQUERY_CLIENT.get_or_create_table(
            table=table,
            ctx=ctx,
        )

        return table

    async def create_bq_view(self, *, handle: BigQueryView, ctx: LogContext) -> None:
        async with database.async_session.begin() as db_session:
            existing_vevent = (
                await VirtualEventOrm.query(
                    session=db_session,
                    params=VirtualEventOrm.QueryParams(
                        team_id=self._client.team_id,
                        view_id=handle.view_id,
                    ),
                )
            ).one_or_none()

            if existing_vevent:
                return

            try:
                handle.sync(ctx=ctx)

                await VirtualEventOrm.create(
                    session=db_session,
                    team_id=self._client.team_id,
                    view_id=handle.view_id,
                    readable_name=handle.friendly_name,
                    description=handle.description,
                )
            except Exception as e:
                # Likely a race condition: Two events came in separate requests that tried to create the same virtual event.
                # Or the request to BQ failed.
                LOGGER.exception(e, ctx)
