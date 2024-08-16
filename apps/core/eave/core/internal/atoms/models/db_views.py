from abc import ABC, abstractmethod
from dataclasses import dataclass
from textwrap import dedent
from typing import cast

import inflect
from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.collectors.core.datastructures import DatabaseOperation
from eave.core.internal.atoms.models.api_payload_types import BrowserAction
from eave.core.internal.atoms.models.atom_types import BrowserEventAtom, DatabaseEventAtom
from eave.stdlib.core_api.models.virtual_event import BigQueryFieldMode
from eave.stdlib.util import sql_sanitized_identifier, sql_sanitized_literal, tableize, titleize


@dataclass(kw_only=True, frozen=True)
class ViewField:
    definition: str
    alias: str
    description: str
    field_type: SqlTypeNames

    @property
    def selector(self) -> str:
        return f"{self.definition} as {self.alias}"

    @property
    def schema_field(self) -> SchemaField:
        return SchemaField(
            name=self.alias,
            description=self.description,
            field_type=self.field_type,
            mode=BigQueryFieldMode.NULLABLE,  # view fields are always nullable
        )


_COMMON_VIEW_FIELDS = (
    ViewField(
        definition=sql_sanitized_identifier("timestamp"),
        alias="event_timestamp",
        description="The UTC date and time at which this event occurred.",
        field_type=SqlTypeNames.TIMESTAMP,
    ),
    ViewField(
        definition="account.account_id",
        alias="account_id",
        description="The logged-in account ID of the user who performed this action. For anonymous users, this is null.",
        field_type=SqlTypeNames.STRING,
    ),
    ViewField(
        definition="visitor_id",
        alias="visitor_id",
        description="The unique device ID of the user who performed this action. This is set on their first visit to the page.",
        field_type=SqlTypeNames.STRING,
    ),
    ViewField(
        definition="session.id",
        alias="session_id",
        description="The ID of the session during which this event occurred.",
        field_type=SqlTypeNames.STRING,
    ),
    ViewField(
        definition="session.start_timestamp",
        alias="session_start_timestamp",
        description="The start timestamp of the session during which this event occurred.",
        field_type=SqlTypeNames.TIMESTAMP,
    ),
    ViewField(
        definition="session.duration_ms",
        alias="session_duration_ms",
        description="The duration of the session at the time this event occurred.",
        field_type=SqlTypeNames.FLOAT,
    ),
    ViewField(
        definition="traffic_source.utm_campaign",
        alias="utm_campaign",
        description="Query parameter 'utm_campaign'.",
        field_type=SqlTypeNames.STRING,
    ),
    ViewField(
        definition="traffic_source.utm_medium",
        alias="utm_medium",
        description="Query parameter 'utm_medium'.",
        field_type=SqlTypeNames.STRING,
    ),
    ViewField(
        definition="traffic_source.utm_source",
        alias="utm_source",
        description="Query parameter 'utm_source'.",
        field_type=SqlTypeNames.STRING,
    ),
    ViewField(
        definition="traffic_source.utm_term",
        alias="utm_term",
        description="Query parameter 'utm_term'.",
        field_type=SqlTypeNames.STRING,
    ),
    ViewField(
        definition="traffic_source.utm_content",
        alias="utm_content",
        description="Query parameter 'utm_content'.",
        field_type=SqlTypeNames.STRING,
    ),
)

_COMMON_GEO_FIELDS = (
    ViewField(
        definition="geo.region",
        alias="geo_region",
        description="The country (or region) associated with the client's IP address. CLDR region code. https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2",
        field_type=SqlTypeNames.STRING,
    ),
    ViewField(
        definition="geo.subdivision",
        alias="geo_subdivision",
        description="Subdivision, for example, a province or state, of the country associated with the client's IP address. CLDR subdivision ID. https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2",
        field_type=SqlTypeNames.STRING,
    ),
    ViewField(
        definition="geo.city",
        alias="geo_city",
        description="Name of the city associated with the client's IP address.",
        field_type=SqlTypeNames.STRING,
    ),
    ViewField(
        definition="client_ip",
        alias="ip_address",
        description="IP address of the client.",
        field_type=SqlTypeNames.STRING,
    ),
)

_COMMON_DEVICE_FIELDS = (
    ViewField(
        definition="device.platform",
        alias="device_os",
        description="The device Operating System name.",
        field_type=SqlTypeNames.STRING,
    ),
    ViewField(
        definition="device.platform_version",
        alias="device_os_version",
        description="The Operating System version of the device.",
        field_type=SqlTypeNames.STRING,
    ),
    ViewField(
        definition="device.mobile",
        alias="device_mobile",
        description="Whether the device is a mobile device.",
        field_type=SqlTypeNames.BOOLEAN,
    ),
    ViewField(
        definition="device.form_factor",
        alias="device_form_factor",
        description="The device form-factor. e.g. 'Tablet', 'VR'",
        field_type=SqlTypeNames.STRING,
    ),
    ViewField(
        definition="device.model",
        alias="device_model",
        description="The mobile device model name, if device is mobile. e.g. 'Pixel 2XL'",
        field_type=SqlTypeNames.STRING,
    ),
    ViewField(
        # the first brand that isn't "Chromium" or "Not A Brand";
        # aka hopefully the common name of the browser
        definition=dedent("""
            (SELECT brand
            FROM UNNEST(device.brands) AS brand_record
            WHERE NOT REGEXP_CONTAINS(brand_record.brand, r"Chromium|Not.A.Brand")
            ORDER BY brand_record.version DESC
            LIMIT 1)
            """).strip(),
        alias="device_browser_name",
        description="The brand name of the browser client.",
        field_type=SqlTypeNames.STRING,
    ),
    ViewField(
        # version of first brand that isn't "Chromium" or "Not A Brand";
        # aka hopefully the actual browser version
        definition=dedent("""
            (SELECT version
            FROM UNNEST(device.brands) AS brand_record
            WHERE NOT REGEXP_CONTAINS(brand_record.brand, r"Chromium|Not.A.Brand")
            ORDER BY brand_record.version DESC
            LIMIT 1)
            """).strip(),
        alias="device_browser_version",
        description="The version number of the browser client.",
        field_type=SqlTypeNames.STRING,
    ),
)

_COMMON_CURRENT_PAGE_FIELDS = (
    ViewField(
        definition="current_page.title",
        alias="current_page_title",
        description="The title of the page on which this event occurred.",
        field_type=SqlTypeNames.STRING,
    ),
    ViewField(
        definition="current_page.url.path",
        alias="current_page_path",
        description="The path of the page on which this event occurred.",
        field_type=SqlTypeNames.STRING,
    ),
    ViewField(
        definition="current_page.url.hash",
        alias="current_page_hash",
        description="The URL hash of the page on which this event occurred.",
        field_type=SqlTypeNames.STRING,
    ),
    ViewField(
        definition="current_page.url.domain",
        alias="current_page_domain",
        description="The URL domain of the page on which this event occurred.",
        field_type=SqlTypeNames.STRING,
    ),
)

_COMMON_BROWSER_EVENT_FIELDS = (
    *_COMMON_VIEW_FIELDS,
    *_COMMON_CURRENT_PAGE_FIELDS,
    *_COMMON_DEVICE_FIELDS,
    *_COMMON_GEO_FIELDS,
)


class BigQueryViewDefinition(ABC):
    view_id: str
    """The BigQuery table ID"""

    friendly_name: str
    """Friendly name for BigQuery table metadata"""

    description: str
    """Description for BigQuery table metadata"""

    @property
    @abstractmethod
    def schema(self) -> tuple[ViewField, ...]:
        """The schema for the view query. Its only purpose is to provide field descriptions. Not authoritative. This must match the view query."""
        ...

    @abstractmethod
    def build_view_query(self, *, dataset_id: str) -> str:
        """The SQL query that defines this view. Authoritative for the schema."""
        ...

    @property
    def schema_fields(self) -> tuple[SchemaField, ...]:
        return tuple(f.schema_field for f in self.schema)

    @property
    def compiled_selectors(self) -> str:
        return ",\n    ".join(f.selector for f in self.schema)

    def sql_sanitized_fq_table(self, *, dataset_id: str, table_id: str) -> str:
        sanitized_dataset_id = sql_sanitized_identifier(dataset_id)
        sanitized_table_id = sql_sanitized_identifier(table_id)
        return f"{sanitized_dataset_id}.{sanitized_table_id}"


_db_operation_to_past_tense_verb = {
    DatabaseOperation.INSERT: "created",
    DatabaseOperation.UPDATE: "updated",
    DatabaseOperation.DELETE: "deleted",
    DatabaseOperation.SELECT: "queried",
}


class DatabaseEventView(BigQueryViewDefinition):
    _event_table_name: str
    _event_operation: DatabaseOperation

    def __init__(self, *, event_table_name: str, event_operation: DatabaseOperation) -> None:
        table_resource = titleize(event_table_name)
        operation_past_tense_verb: str | None = _db_operation_to_past_tense_verb.get(event_operation)
        name_verb = (operation_past_tense_verb or event_operation).title()
        friendly_name = f"{table_resource} {name_verb}"
        view_id = tableize(string=friendly_name)

        if operation_past_tense_verb:
            inflect_engine = inflect.engine()
            # Word is a string with len >= 1, which is always true here, so we just cast instead of assert for better performance.
            aresource = inflect_engine.a(cast(inflect.Word, table_resource))
            description = f"{aresource.title()} was {operation_past_tense_verb}."
        else:
            description = friendly_name

        self.view_id = view_id
        self.friendly_name = friendly_name
        self.description = description
        self._event_table_name = event_table_name
        self._event_operation = event_operation

    @property
    def schema(self) -> tuple[ViewField, ...]:
        sanitized_friendly_name = sql_sanitized_literal(self.friendly_name)

        return (
            ViewField(
                definition=sanitized_friendly_name,
                alias="event_name",
                description=f"The readable name for this event. Always {sanitized_friendly_name}.",
                field_type=SqlTypeNames.STRING,
            ),
            *_COMMON_VIEW_FIELDS,
        )

    def build_view_query(self, *, dataset_id: str) -> str:
        sanitized_fq_source_table = self.sql_sanitized_fq_table(
            dataset_id=dataset_id,
            table_id=DatabaseEventAtom.table_def().table_id,
        )
        sanitized_db_event_table = sql_sanitized_literal(self._event_table_name)
        sanitized_db_event_operation = sql_sanitized_literal(self._event_operation)

        return dedent(
            f"""
            SELECT
                {self.compiled_selectors}
            FROM
                {sanitized_fq_source_table}
            WHERE
                `table_name` = {sanitized_db_event_table}
                AND `operation` = {sanitized_db_event_operation}
            ORDER BY
                `event_timestamp` ASC
            """
        ).strip()


class ClickView(BigQueryViewDefinition):
    # This view is the same for all customers, so we hardcode the fields.
    view_id = "click"
    friendly_name = "Click Event"
    description = "A user clicked an element."

    @property
    def schema(self) -> tuple[ViewField, ...]:
        sanitized_event_name = sql_sanitized_literal("Click")
        return (
            ViewField(
                definition=sanitized_event_name,
                alias="event_name",
                description=f"The readable name for this event. Always {sanitized_event_name}.",
                field_type=SqlTypeNames.STRING,
            ),
            ViewField(
                definition=dedent("""
                CASE
                    WHEN target.type = 'IMG' THEN 'IMAGE'
                    WHEN target.type = 'CIRCLE' THEN 'IMAGE'
                    WHEN target.type = 'ELLIPSE' THEN 'IMAGE'
                    WHEN target.type = 'LINE' THEN 'IMAGE'
                    WHEN target.type = 'PATH' THEN 'IMAGE'
                    WHEN target.type = 'POLYGON' THEN 'IMAGE'
                    WHEN target.type = 'POLYLINE' THEN 'IMAGE'
                    WHEN target.type = 'RECT' THEN 'IMAGE'
                    WHEN target.type = 'SVG' THEN 'IMAGE'
                    WHEN target.type = 'A' THEN 'LINK'
                    WHEN target.type = 'DIV' THEN 'CONTAINER'
                    WHEN target.type = 'SPAN' THEN 'TEXT'
                    WHEN target.type = 'H1' THEN 'TEXT'
                    WHEN target.type = 'H2' THEN 'TEXT'
                    WHEN target.type = 'H3' THEN 'TEXT'
                    WHEN target.type = 'H4' THEN 'TEXT'
                    WHEN target.type = 'H5' THEN 'TEXT'
                    WHEN target.type = 'H6' THEN 'TEXT'
                    WHEN target.type = 'P' THEN 'TEXT'
                    WHEN target.type = 'STRONG' THEN 'TEXT'
                    WHEN target.type = 'EM' THEN 'TEXT'
                    WHEN target.type = 'I' THEN 'TEXT'
                    WHEN target.type = 'S' THEN 'TEXT'
                    WHEN target.type = 'SUP' THEN 'TEXT'
                    WHEN target.type = 'SUB' THEN 'TEXT'
                    WHEN target.type = 'B' THEN 'TEXT'
                    WHEN target.type = 'LI' THEN 'TEXT'
                    WHEN target.type = 'U' THEN 'TEXT'
                    WHEN target.type = 'OL' THEN 'TEXT'
                    WHEN target.type = 'UL' THEN 'TEXT'
                    WHEN target.type = 'BR' THEN 'LINE BREAK'
                    WHEN target.type = 'TD' THEN 'TABLE CELL'
                    WHEN target.type = 'TR' THEN 'TABLE ROW'
                    WHEN target.type = 'TH' THEN 'TABLE HEADER CELL'
                    WHEN target.type = 'THEAD' THEN 'TABLE HEADER'
                    WHEN target.type = 'TFOOT' THEN 'TABLE FOOTER'
                    ELSE target.type
                END
                """).strip(),
                alias="target_type",
                description="The friendly name of the clicked HTML element. eg: IMAGE, LINK, BUTTON.",
                field_type=SqlTypeNames.STRING,
            ),
            ViewField(
                definition="target.id",
                alias="target_id",
                description="The HTML ID attribute of the clicked element.",
                field_type=SqlTypeNames.STRING,
            ),
            ViewField(
                definition="target.content",
                alias="target_content",
                description="The inner content of the clicked element. Depends on the target type. For buttons and links, this is the button/link text. For images, it is the image source URL.",
                field_type=SqlTypeNames.STRING,
            ),
            *_COMMON_BROWSER_EVENT_FIELDS,
        )

    def build_view_query(self, *, dataset_id: str) -> str:
        sanitized_fq_source_table = self.sql_sanitized_fq_table(
            dataset_id=dataset_id,
            table_id=BrowserEventAtom.table_def().table_id,
        )

        sanitized_action_name = sql_sanitized_literal(BrowserAction.CLICK)

        return dedent(
            f"""
            SELECT
                {self.compiled_selectors}
            FROM
                {sanitized_fq_source_table}
            WHERE
                `action` = {sanitized_action_name}
            ORDER BY
                `event_timestamp` ASC
            """
        ).strip()


class FormSubmissionView(BigQueryViewDefinition):
    # This view is the same for all customers, so we hardcode the fields.
    view_id = "form_submission"
    friendly_name = "Form Submission Event"
    description = "A user submitted a form."

    @property
    def schema(self) -> tuple[ViewField, ...]:
        sanitized_event_name = sql_sanitized_literal("Form Submission")

        return (
            ViewField(
                definition=sanitized_event_name,
                alias="event_name",
                description=f"The readable name for this event. Always {sanitized_event_name}.",
                field_type=SqlTypeNames.STRING,
            ),
            ViewField(
                definition="target.id",
                alias="form_id",
                description="The HTML ID attribute of the submitted form.",
                field_type=SqlTypeNames.STRING,
            ),
            ViewField(
                definition="target.content",
                alias="form_action",
                description="The URL to which the form data is submitted. This is null for forms managed by javascript.",
                field_type=SqlTypeNames.STRING,
            ),
            *_COMMON_BROWSER_EVENT_FIELDS,
        )

    def build_view_query(self, *, dataset_id: str) -> str:
        sanitized_fq_source_table = self.sql_sanitized_fq_table(
            dataset_id=dataset_id,
            table_id=BrowserEventAtom.table_def().table_id,
        )

        sanitized_action_name = sql_sanitized_literal(BrowserAction.FORM_SUBMISSION)

        return dedent(
            f"""
            SELECT
                {self.compiled_selectors}
            FROM
                {sanitized_fq_source_table}
            WHERE
                `action` = {sanitized_action_name}
            ORDER BY
                `event_timestamp` ASC
            """
        ).strip()


class PageViewView(BigQueryViewDefinition):
    # This view is the same for all customers, so we hardcode the fields.
    view_id = "page_view"
    friendly_name = "Page View Event"
    description = "A user navigated to a new location in their browser."

    @property
    def schema(self) -> tuple[ViewField, ...]:
        sanitized_event_name = sql_sanitized_literal("Page View")

        return (
            ViewField(
                definition=sanitized_event_name,
                alias="event_name",
                description=f"The readable name for this event. Always {sanitized_event_name}.",
                field_type=SqlTypeNames.STRING,
            ),
            *_COMMON_BROWSER_EVENT_FIELDS,
        )

    def build_view_query(self, *, dataset_id: str) -> str:
        sanitized_fq_source_table = self.sql_sanitized_fq_table(
            dataset_id=dataset_id,
            table_id=BrowserEventAtom.table_def().table_id,
        )

        sanitized_action_name = sql_sanitized_literal(BrowserAction.PAGE_VIEW)

        return dedent(
            f"""
            WITH EventGroups AS (
                SELECT
                    *,
                    CASE
                        WHEN action = {sanitized_action_name} AND
                            LAG(action) OVER (PARTITION BY visitor_id, session.id ORDER BY timestamp) = {sanitized_action_name}
                        THEN 0
                        ELSE 1
                    END AS grp_start
                FROM {sanitized_fq_source_table}
            ),
            RankedEvents AS (
                SELECT
                    *,
                    SUM(grp_start) OVER (PARTITION BY visitor_id, session.id ORDER BY timestamp) AS grp
                FROM EventGroups
            ),
            FilteredEvents AS (
                SELECT
                    *,
                    ROW_NUMBER() OVER (PARTITION BY visitor_id, session.id, grp ORDER BY timestamp DESC) AS rn
                FROM RankedEvents
                WHERE `action` = {sanitized_action_name}
            )
            SELECT
                {self.compiled_selectors}
            FROM FilteredEvents
            WHERE rn = 1
            ORDER BY
                `event_timestamp` ASC
            """
        ).strip()
