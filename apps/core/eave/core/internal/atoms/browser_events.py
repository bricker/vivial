from dataclasses import dataclass
from textwrap import dedent
from typing import Any, cast

from eave.collectors.core.datastructures import BrowserEventPayload, Geolocation
from eave.stdlib.typing import JsonObject

from eave.core.internal import database

from eave.stdlib.util import sql_sanitized_identifier, sql_sanitized_literal, tableize, titleize
from google.cloud.bigquery import SchemaField, SqlTypeNames, StandardSqlTypeNames

from eave.stdlib.logging import LOGGER, LogContext

from eave.core.internal.atoms.shared import discovery_field, insert_timestamp_field, key_value_record_field, session_field, timestamp_field, user_field
from eave.core.internal.orm.virtual_event import VirtualEventOrm

from .table_handle import BigQueryFieldMode, BigQueryTableDefinition, BigQueryTableHandle

_HTML_TAG_READABLE_NAMES = {
    "A": "Link",
    "BUTTON": "Button",
    "IMG": "Image",
    "H1": "Header",
    "H2": "Header",
    "H3": "Header",
    "H4": "Header",
    "H5": "Header",
    "H6": "Header",
    "P": "Text",
}

class BrowserEventsTableHandle(BigQueryTableHandle):
    table_def = BigQueryTableDefinition(
        table_id="atoms_browser_events_v1",
        description="Browser atoms",
        schema=(
            SchemaField(
                name="action",
                description="The user action that caused this event.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),

            timestamp_field(),
            session_field(),
            user_field(),
            discovery_field(),

            SchemaField(
                name="target",
                description="Information about the event target, when applicable. Generally, a target will be a DOM element.",
                field_type=SqlTypeNames.RECORD,
                mode=BigQueryFieldMode.NULLABLE,
                fields=(
                    SchemaField(
                        name="type",
                        description="The type of target. For DOM elements, this is the tag name.",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="id",
                        description="An ID for this target. For DOM elements, this is the 'id' attribute.",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="text",
                        description="The text inside of this target. For DOM elements, this is the 'innerText' attribute.",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),

                    key_value_record_field(name="attributes", description="All attributes explicitly defined on this target in the DOM."),
                ),
            ),

            SchemaField(
                name="page",
                description="Properties about the current page at the time this event occurred.",
                field_type=SqlTypeNames.RECORD,
                mode=BigQueryFieldMode.NULLABLE,
                fields=(
                    SchemaField(
                        name="current_url",
                        description="The page URL when this event occurred.",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="current_title",
                        description="The page title when this event occurred.",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="pageview_id",
                        description="A unique ID for this page view. Unique per document load.",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),

                    key_value_record_field(name="current_query_params", description="The URL query parameters when this event occurred."),
                ),
            ),

            SchemaField(
                name="device",
                description="Browser Device information. Depending on browser and permissions, some data may not be available.",
                field_type=SqlTypeNames.RECORD,
                mode=BigQueryFieldMode.NULLABLE,
                fields=(
                    SchemaField(
                        name="user_agent",
                        description="https://developer.mozilla.org/en-US/docs/Web/API/Navigator/userAgent",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="brands",
                        description="https://developer.mozilla.org/en-US/docs/Web/API/NavigatorUAData/brands",
                        field_type=SqlTypeNames.RECORD,
                        mode=BigQueryFieldMode.REPEATED,
                        fields=(
                            SchemaField(
                                name="brand",
                                description="https://developer.mozilla.org/en-US/docs/Web/API/NavigatorUAData/brands#brand",
                                field_type=SqlTypeNames.STRING,
                                mode=BigQueryFieldMode.NULLABLE,
                            ),
                            SchemaField(
                                name="version",
                                description="https://developer.mozilla.org/en-US/docs/Web/API/NavigatorUAData/brands#version",
                                field_type=SqlTypeNames.STRING,
                                mode=BigQueryFieldMode.NULLABLE,
                            ),
                        ),
                    ),
                    SchemaField(
                        name="platform",
                        description="https://developer.mozilla.org/en-US/docs/Web/API/NavigatorUAData/platform",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="platform_version",
                        description="https://developer.mozilla.org/en-US/docs/Web/API/NavigatorUAData/getHighEntropyValues#platformversion",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="mobile",
                        description="https://developer.mozilla.org/en-US/docs/Web/API/NavigatorUAData/mobile",
                        field_type=SqlTypeNames.BOOLEAN,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="form_factor",
                        description="https://developer.mozilla.org/en-US/docs/Web/API/NavigatorUAData/getHighEntropyValues#formfactor",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="model",
                        description="https://developer.mozilla.org/en-US/docs/Web/API/NavigatorUAData/getHighEntropyValues#model",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="screen_width",
                        description="https://developer.mozilla.org/en-US/docs/Web/API/Screen/width",
                        field_type=SqlTypeNames.INTEGER,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="screen_height",
                        description="https://developer.mozilla.org/en-US/docs/Web/API/Screen/height",
                        field_type=SqlTypeNames.INTEGER,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="screen_avail_width",
                        description="https://developer.mozilla.org/en-US/docs/Web/API/Screen/availWidth",
                        field_type=SqlTypeNames.INTEGER,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="screen_avail_height",
                        description="https://developer.mozilla.org/en-US/docs/Web/API/Screen/availHeight",
                        field_type=SqlTypeNames.INTEGER,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                ),
            ),

            SchemaField(
                name="geo",
                description="Geography information about the client.",
                field_type=SqlTypeNames.RECORD,
                mode=BigQueryFieldMode.NULLABLE,
                fields=(
                    SchemaField(
                        name="region",
                        description="The country (or region) associated with the client's IP address. CLDR region code. https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="subdivision",
                        description="Subdivision, for example, a province or state, of the country associated with the client's IP address. CLDR subdivision ID. https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="city",
                        description="Name of the city from which the request originated.",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                    SchemaField(
                        name="coordinates",
                        description="Latitude and Longitude of the city from which the request originated.",
                        field_type=SqlTypeNames.STRING,
                        mode=BigQueryFieldMode.NULLABLE,
                    ),
                ),
            ),

            key_value_record_field(name="extra", description="Arbitrary event-specific parameters."),

            SchemaField(
                name="client_ip",
                description="The user's IP address.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),

            insert_timestamp_field(),
        ),
    )

    async def insert(self, events: list[dict[str, Any]], ctx: LogContext) -> None:
        await self.insert_with_geolocation(events, geolocation=None, client_ip=None, ctx=ctx)

    async def insert_with_geolocation(self, events: list[dict[str, Any]], geolocation: Geolocation | None, client_ip: str | None, ctx: LogContext) -> None:
        if len(events) == 0:
            return

        dataset = self._bq_client.get_or_create_dataset(
            dataset_id=self.team.bq_dataset_id,
        )

        table = self._bq_client.get_and_sync_or_create_table(
            dataset_id=dataset.dataset_id,
            table_id=self.table_def.table_id,
            schema=self.table_def.schema,
            description=self.table_def.description,
            ctx=ctx,
        )

        unique_operations: set[str] = set()
        formatted_rows: list[dict[str, Any]] = []

        browser_events = [BrowserEventPayload(**e) for e in events]

        for e in browser_events:
            if e.action is None:
                LOGGER.warning("event action unexpectedly None", ctx)
                continue

            unique_operations.add(e.action)

            if geolocation and e.geo is None:
                e.geo = geolocation

            if client_ip and e.client_ip is None:
                e.client_ip = client_ip

            formatted_rows.append(e.to_dict())

        errors = self._bq_client.append_rows(
            table=table,
            rows=formatted_rows,
        )

        if len(errors) > 0:
            LOGGER.warning("BigQuery insert errors", {"errors": cast(list, errors)}, ctx)

        # FIXME: This is vulnerable to a DoS
        for action in unique_operations:
            await self._create_vevent_view(action=action, ctx=ctx)

    async def _create_vevent_view(self, *, action: str, ctx: LogContext) -> None:
        vevent_readable_name = titleize(action)
        vevent_view_id = tableize(vevent_readable_name)

        async with database.async_session.begin() as db_session:
            vevent_query = (await VirtualEventOrm.query(
                session=db_session,
                params=VirtualEventOrm.QueryParams(
                    team_id=self.team.id,
                    view_id=vevent_view_id,
                ),
            )).one_or_none()

            sanitized_dataset_id=sql_sanitized_identifier(self.team.bq_dataset_id)
            sanitized_atom_table_id=sql_sanitized_identifier(self.table_def.table_id)
            sanitized_action=sql_sanitized_literal(action)

            fields = (
                SchemaField(
                    name="action",
                    description="The user action that triggered this event.",
                    field_type=SqlTypeNames.STRING
                )
            )

            table = self._bq_client.construct_table(dataset_id=self.team.bq_dataset_id, table_id=vevent_view_id)
            table.friendly_name = vevent_readable_name
            table.description=vevent_readable_name
            table.mview_query = dedent(
                f"""
                SELECT
                    {vevent_readable_name} as event_name,
                    action,
                    target,
                    extra,
                    page,
                    user,
                    session,
                    discovery,
                    geo,
                    device
                FROM
                    {sanitized_dataset_id}.{sanitized_atom_table_id}
                WHERE
                    `action` = {sanitized_action}
                ORDER BY
                    `timestamp` ASC
                """
            ).strip()

            table.schema = (
                SchemaField(
                    name="event_name",
                    description=f"A readable name for this event. Always '{vevent_readable_name}'.",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.REQUIRED,
                ),
                SchemaField(
                    name="action",
                    description=f"The user action that triggered this event. Always '{action}'.",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.REQUIRED,
                ),
            )

            # self._bq_client.get_and_sync_or_create_view(
            #     dataset_id=self.team.bq_dataset_id,
            #     view_id=vevent_view_id,
            #     description=vevent_readable_name,
            #     mview_query=dedent(
            #         f"""
            #         SELECT
            #             {vevent_readable_name} as event_name,
            #             action,
            #             target,
            #             extra,
            #             page,
            #             user,
            #             session,
            #             discovery,
            #             geo,
            #             device
            #         FROM
            #             {sanitized_dataset_id}.{sanitized_atom_table_id}
            #         WHERE
            #             `action` = {sanitized_action}
            #         ORDER BY
            #             `timestamp` ASC
            #         """
            #     ).strip(),
            #     schema=()
            # )

            await VirtualEventOrm.create(
                session=db_session,
                team_id=self.team.id,
                view_id=vevent_view_id,
                readable_name=vevent_readable_name,
                description=f"User {vevent_readable_name} in the browser.",
                fields=[]
            )

def _action_readable_verb_past_tense(action: str) -> str:
    return title
    match action.upper():
        case "CLICK":

    pass