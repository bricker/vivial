from google.cloud.bigquery import Table

from eave.core.internal import database
from eave.core.internal.atoms.models.atom_types import BigQueryTableDefinition
from eave.core.internal.atoms.models.db_record_fields import MetadataRecordField
from eave.core.internal.atoms.models.db_views import BigQueryViewDefinition
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm
from eave.core.internal.orm.team import bq_dataset_id
from eave.core.internal.orm.virtual_event import VirtualEventOrm
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.logging import LOGGER, LogContext


class BaseAtomController:
    _dataset_id: str
    _client: ClientCredentialsOrm

    def __init__(self, *, client: ClientCredentialsOrm) -> None:
        self._client = client
        self._dataset_id = bq_dataset_id(client.team_id)

    @staticmethod
    def get_record_metadata() -> MetadataRecordField:
        return MetadataRecordField(
            source_app_name=SHARED_CONFIG.app_service,
            source_app_version=SHARED_CONFIG.app_version,
            source_app_release_timestamp=SHARED_CONFIG.release_timestamp,
        )

    def get_or_create_bq_table(self, *, table_def: BigQueryTableDefinition, ctx: LogContext) -> Table:
        # Lazily creates the dataset in case it doesn't exist.
        EAVE_INTERNAL_BIGQUERY_CLIENT.get_or_create_dataset(dataset_id=self._dataset_id)

        table = EAVE_INTERNAL_BIGQUERY_CLIENT.construct_table(dataset_id=self._dataset_id, table_id=table_def.table_id)
        table.description = table_def.description
        table.friendly_name = table_def.friendly_name
        table.schema = table_def.schema

        table = EAVE_INTERNAL_BIGQUERY_CLIENT.get_or_create_table(
            table=table,
            ctx=ctx,
        )

        return table

    async def sync_bq_view(self, *, view_def: BigQueryViewDefinition, ctx: LogContext) -> None:
        async with database.async_session.begin() as db_session:
            existing_vevent = (
                await VirtualEventOrm.query(
                    session=db_session,
                    params=VirtualEventOrm.QueryParams(
                        team_id=self._client.team_id,
                        view_id=view_def.view_id,
                    ),
                )
            ).one_or_none()

            try:
                EAVE_INTERNAL_BIGQUERY_CLIENT.get_and_sync_or_create_view(
                    dataset_id=self._dataset_id,
                    view_id=view_def.view_id,
                    friendly_name=view_def.friendly_name,
                    description=view_def.description,
                    view_query=view_def.build_view_query(dataset_id=self._dataset_id),
                    schema=view_def.schema_fields,
                    ctx=ctx,
                )

                if not existing_vevent:
                    # virtual event view in bq needs a new entry in eave db
                    await VirtualEventOrm.create(
                        session=db_session,
                        team_id=self._client.team_id,
                        view_id=view_def.view_id,
                        readable_name=view_def.friendly_name,
                        description=view_def.description,
                    )

            except Exception as e:
                # Likely a race condition: Two events came in separate requests that tried to create the same virtual event.
                # Or the request to BQ failed.
                LOGGER.exception(e, ctx)
