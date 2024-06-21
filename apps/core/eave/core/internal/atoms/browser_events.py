import dataclasses
from dataclasses import dataclass
from textwrap import dedent
from typing import Any, Self, cast

from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.core.internal import database
from eave.core.internal.atoms.api_types import BrowserAction, BrowserEventPayload
from eave.core.internal.atoms.record_fields import (
    CurrentPageRecordField,
    DeviceRecordField,
    GeoRecordField,
    MultiScalarTypeKeyValueRecordField,
    SessionRecordField,
    TargetRecordField,
    TrafficSourceRecordField,
    UserRecordField,
)
from eave.core.internal.orm.virtual_event import VirtualEventOrm
from eave.stdlib.logging import LOGGER, LogContext
from eave.stdlib.util import sql_sanitized_identifier, sql_sanitized_literal, tableize, titleize

from .shared import common_bq_insert_timestamp_field, common_event_timestamp_field, Redactable
from .table_handle import BigQueryFieldMode, BigQueryTableDefinition, BigQueryTableHandle


@dataclass(kw_only=True)
class BrowserEventAtom(Redactable):
    @staticmethod
    def schema() -> tuple[SchemaField, ...]:
        return (
            SchemaField(
                name="action",
                description="The user action that caused this event.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            common_event_timestamp_field(),
            SessionRecordField.schema(),
            UserRecordField.schema(),
            TrafficSourceRecordField.schema(),
            TargetRecordField.schema(),
            CurrentPageRecordField.schema(),
            DeviceRecordField.schema(),
            GeoRecordField.schema(),
            MultiScalarTypeKeyValueRecordField.schema(
                name="extra",
                description="Arbitrary event-specific parameters.",
            ),
            SchemaField(
                name="client_ip",
                description="The user's IP address.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            common_bq_insert_timestamp_field(),
        )

    action: str | None
    timestamp: float | None
    session: SessionRecordField | None
    user: UserRecordField | None
    traffic_source: TrafficSourceRecordField | None
    target: TargetRecordField | None
    current_page: CurrentPageRecordField | None
    device: DeviceRecordField | None
    geo: GeoRecordField | None
    extra: list[MultiScalarTypeKeyValueRecordField] | None
    client_ip: str | None

    def redact_sensitive_content(self) -> Self:
        if self.target:
            self.target.redact_sensitive_content()
        if self.current_page:
            self.current_page.redact_sensitive_content()
        # TODO: add some config for whether to do geo data redaction?
        # if self.geo:
        #     self.geo.redact_sensitive_content()
        # if self.client_ip:
        #     self.client_ip = "*****"
        if self.extra:
            for item in self.extra:
                item.redact_sensitive_content()
        return self


class BrowserEventsTableHandle(BigQueryTableHandle):
    table_def = BigQueryTableDefinition(
        table_id="atoms_browser_events",
        friendly_name="Browser Atoms",
        description="Browser atoms",
        schema=BrowserEventAtom.schema(),
    )

    async def insert_with_geolocation(
        self, events: list[dict[str, Any]], geolocation: GeoRecordField | None, client_ip: str | None, ctx: LogContext
    ) -> None:
        if len(events) == 0:
            return

        self._bq_client.get_or_create_dataset(dataset_id=self.dataset_id)

        table = self._bq_client.get_or_create_table(
            table=self.construct_bq_table(),
            ctx=ctx,
        )

        unique_operations: set[BrowserAction] = set()
        atoms: list[BrowserEventAtom] = []

        for payload in events:
            e = BrowserEventPayload.from_api_payload(payload)
            if not e.action:
                LOGGER.warning("Unexpected event action", {"event": payload}, ctx)
                continue

            unique_operations.add(e.action)

            session = (
                SessionRecordField.from_api_resource(resource=e.corr_ctx.session, event_timestamp=e.timestamp)
                if e.corr_ctx
                else None
            )
            traffic_source = (
                TrafficSourceRecordField.from_api_resource(e.corr_ctx.traffic_source) if e.corr_ctx else None
            )
            user = (
                UserRecordField(account_id=e.corr_ctx.account_id, visitor_id=e.corr_ctx.visitor_id)
                if e.corr_ctx
                else None
            )

            atom = BrowserEventAtom(
                action=e.action,
                timestamp=e.timestamp,
                session=session,
                user=user,
                traffic_source=traffic_source,
                target=TargetRecordField.from_api_resource(e.target),
                current_page=CurrentPageRecordField.from_api_resource(e.current_page),
                device=DeviceRecordField.from_api_resource(e.device),
                geo=geolocation,
                extra=MultiScalarTypeKeyValueRecordField.list_from_scalar_dict(e.extra),
                client_ip=client_ip,
            )
            atom.redact_sensitive_content()

            atoms.append(atom)

        formatted_rows = [dataclasses.asdict(atom) for atom in atoms]
        errors = self._bq_client.append_rows(
            table=table,
            rows=formatted_rows,
        )

        if len(errors) > 0:
            LOGGER.warning("BigQuery insert errors", {"errors": cast(list, errors)}, ctx)

        for action in unique_operations:
            await self._create_vevent_view(action=action, ctx=ctx)

    async def _create_vevent_view(self, *, action: str, ctx: LogContext) -> None:
        vevent_readable_name = titleize(action)
        vevent_description = _make_vevent_description(action) or vevent_readable_name
        vevent_view_id = tableize(vevent_readable_name)

        async with database.async_session.begin() as db_session:
            existing_vevent = (
                await VirtualEventOrm.query(
                    session=db_session,
                    params=VirtualEventOrm.QueryParams(
                        team_id=self.team.id,
                        view_id=vevent_view_id,
                    ),
                )
            ).one_or_none()

            if existing_vevent:
                return

            sanitized_dataset_id = sql_sanitized_identifier(self.dataset_id)
            sanitized_atom_table_id = sql_sanitized_identifier(self.table_def.table_id)
            sanitized_action = sql_sanitized_literal(action)
            sanitized_readable_name = sql_sanitized_literal(vevent_readable_name)

            view = self._bq_client.construct_table(dataset_id=self.dataset_id, table_id=vevent_view_id)
            view.friendly_name = vevent_readable_name
            view.description = vevent_description

            view.view_query = dedent(
                f"""
                SELECT
                    {sanitized_readable_name} as `event_name`,
                    `timestamp`,
                    `target`,
                    `current_page`,
                    `user`,
                    `session`,
                    `traffic_source`,
                    `geo`,
                    `device`,
                    `extra`,
                FROM
                    {sanitized_dataset_id}.{sanitized_atom_table_id}
                WHERE
                    `action` = {sanitized_action}
                ORDER BY
                    `timestamp` ASC
                """
            ).strip()

            view = self._bq_client.get_or_create_table(
                table=view,
                ctx=ctx,
            )

            # TODO: Figure out a way to share the fields so that they don't have to be defined twice,
            # once in table.view_query and once in table.schema.
            # If they are out of sync, the request to create/update the view will fail.

            view.schema = (
                SchemaField(
                    name="event_name",
                    description=f"A readable name for this event. Always '{vevent_readable_name}'.",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                common_event_timestamp_field(),
                TargetRecordField.schema(),
                CurrentPageRecordField.schema(),
                UserRecordField.schema(),
                SessionRecordField.schema(),
                TrafficSourceRecordField.schema(),
                GeoRecordField.schema(),
                DeviceRecordField.schema(),
                MultiScalarTypeKeyValueRecordField.schema(
                    name="extra",
                    description="Arbitrary event-specific parameters.",
                ),
            )

            # This is necessary to set the descriptions on the fields.
            view = self._bq_client.update_table(table=view, ctx=ctx)

            try:
                await VirtualEventOrm.create(
                    session=db_session,
                    team_id=self.team.id,
                    view_id=view.table_id,
                    readable_name=vevent_readable_name,
                    description=vevent_description,
                )
            except Exception as e:
                # Likely a race condition: Two events came in separate requests that tried to create the same virtual event.
                LOGGER.exception(e)


# _HTML_TAG_READABLE_NAMES = {
#     "A": "link",
#     "BUTTON": "button",
#     "IMG": "image",
#     "H1": "header",
#     "H2": "header",
#     "H3": "header",
#     "H4": "header",
#     "H5": "header",
#     "H6": "header",
#     "P": "text",
# }


def _make_vevent_description(action: str) -> str | None:
    browser_action = BrowserAction.from_str(action)
    match browser_action:
        case BrowserAction.CLICK:
            return "A user clicked an element."
        case BrowserAction.FORM_SUBMIT:
            return "A user submitted a form."
        case BrowserAction.NAVIGATION:
            return "A user navigated to a new location in their browser."
        case _:
            return None
