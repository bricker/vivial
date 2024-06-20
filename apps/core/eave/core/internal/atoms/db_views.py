from abc import ABC, abstractmethod
from dataclasses import dataclass
from textwrap import dedent
from typing import cast

import inflect
from google.cloud.bigquery import SchemaField, SqlTypeNames, Table

from eave.collectors.core.datastructures import DatabaseOperation, HttpRequestMethod
from eave.core.internal.atoms.api_types import BrowserAction
from eave.core.internal.atoms.db_tables import BrowserEventAtom, DatabaseEventAtom, HttpServerEventAtom
from eave.core.internal.atoms.shared import BigQueryFieldMode
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.stdlib.logging import LogContext
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


def _common_view_fields() -> tuple[ViewField, ...]:
    return (
        ViewField(
            definition=sql_sanitized_identifier("timestamp"),
            alias="event_timestamp",
            description="The UTC date and time at which this event occurred.",
            field_type=SqlTypeNames.TIMESTAMP,
        ),
        ViewField(
            definition="user.account_id",
            alias="account_id",
            description="The logged-in account ID of the user who performed this action. For anonymous users, this is null.",
            field_type=SqlTypeNames.STRING,
        ),
        ViewField(
            definition="user.visitor_id",
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
    )


class BigQueryView(ABC):
    view_id: str
    """The BigQuery table ID"""

    friendly_name: str
    """Friendly name for BigQuery table metadata"""

    description: str
    """Description for BigQuery table metadata"""

    dataset_id: str
    """The dataset for this view."""

    @property
    @abstractmethod
    def schema(self) -> tuple[ViewField, ...]:
        """The schema for the view query. Its only purpose is to provide field descriptions. Not authoritative. This must match the view query."""
        ...

    @property
    @abstractmethod
    def view_query(self) -> str:
        """The SQL query that defines this view. Authoritative for the schema."""
        ...

    @property
    def schema_fields(self) -> tuple[SchemaField, ...]:
        return tuple(f.schema_field for f in self.schema)

    @property
    def compiled_selectors(self) -> str:
        return ",\n    ".join(f.selector for f in self.schema)

    def sync(self, *, ctx: LogContext) -> Table:
        bq_view = EAVE_INTERNAL_BIGQUERY_CLIENT.construct_table(
            dataset_id=self.dataset_id,
            table_id=self.view_id,
        )

        bq_view.friendly_name = self.friendly_name
        bq_view.description = self.description
        bq_view.view_query = self.view_query

        bq_view = EAVE_INTERNAL_BIGQUERY_CLIENT.get_or_create_table(
            table=bq_view,
            ctx=ctx,
        )

        bq_view.schema = self.schema
        bq_view = EAVE_INTERNAL_BIGQUERY_CLIENT.update_table(table=bq_view, ctx=ctx)
        return bq_view

    def sql_sanitized_fq_table(self, *, table_id: str) -> str:
        sanitized_dataset_id = sql_sanitized_identifier(self.dataset_id)
        sanitized_table_id = sql_sanitized_identifier(table_id)
        return f"{sanitized_dataset_id}.{sanitized_table_id}"


_db_operation_to_past_tense_verb = {
    DatabaseOperation.INSERT: "created",
    DatabaseOperation.UPDATE: "updated",
    DatabaseOperation.DELETE: "deleted",
    DatabaseOperation.SELECT: "queried",
}


class DatabaseEventView(BigQueryView):
    _event_table_name: str
    _event_operation: DatabaseOperation

    def __init__(self, *, dataset_id: str, event_table_name: str, event_operation: DatabaseOperation) -> None:
        table_resource = titleize(event_table_name)
        operation_past_tense_verb: str | None = _db_operation_to_past_tense_verb.get(event_operation)
        name_verb = (operation_past_tense_verb or event_operation).title()
        friendly_name = f"{table_resource} {name_verb}"
        view_id = tableize(friendly_name)

        if operation_past_tense_verb:
            inflect_engine = inflect.engine()
            # Word is a string with len >= 1, which is always true here, so we just cast instead of assert for better performance.
            aresource = inflect_engine.a(cast(inflect.Word, table_resource))
            description = f"{aresource.title()} was {operation_past_tense_verb}."
        else:
            description = friendly_name

        self.dataset_id = dataset_id
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
            *_common_view_fields(),
        )

    @property
    def view_query(self) -> str:
        sanitized_fq_source_table = self.sql_sanitized_fq_table(
            table_id=DatabaseEventAtom.TABLE_DEF.table_id,
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


class HttpServerEventView(BigQueryView):
    _request_method: HttpRequestMethod

    def __init__(self, *, dataset_id: str, request_method: HttpRequestMethod) -> None:
        self.dataset_id = dataset_id
        self.view_id = f"http_server_{request_method.lower()}"
        self.friendly_name = f"HTTP Server {request_method} Request"
        self.description = f"An HTTP {request_method} request was received by the server."
        self._request_method = request_method

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
            *_common_view_fields(),
        )

    @property
    def view_query(self) -> str:
        sanitized_fq_source_table = self.sql_sanitized_fq_table(
            table_id=HttpServerEventAtom.TABLE_DEF.table_id,
        )
        sanitized_request_method = sql_sanitized_literal(self._request_method)

        return dedent(
            f"""
            SELECT
                {self.compiled_selectors}
            FROM
                {sanitized_fq_source_table}
            WHERE
                `request_method` = {sanitized_request_method}
            ORDER BY
                `event_timestamp` ASC
            """
        ).strip()


class ClickView(BigQueryView):
    def __init__(self, *, dataset_id: str) -> None:
        self.dataset_id = dataset_id

        # This view is the same for all customers, so we hardcode the fields.
        self.view_id = "click"
        self.friendly_name = "Click Event"
        self.description = "A user clicked an element."

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
                definition="target.type",
                alias="target_type",
                description="The uppercased HTML tag name of the clicked element. eg: IMG, A, BUTTON.",
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
                definition="device.platform",
                alias="device_platform",
                description="The operating system of the device that triggered this event. eg: Windows, Linux, iOS, Android. https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Sec-CH-UA-Platform",
                field_type=SqlTypeNames.STRING,
            ),
            ViewField(
                definition="device.model",
                alias="device_mobile_model",
                description="For mobile devices, the model of the device that triggered this event. eg: 'Pixel 3'. For non-mobile devices, this is null.",
                field_type=SqlTypeNames.STRING,
            ),
            *_common_view_fields(),
        )

    @property
    def view_query(self) -> str:
        sanitized_fq_source_table = self.sql_sanitized_fq_table(
            table_id=BrowserEventAtom.TABLE_DEF.table_id,
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


class FormSubmissionView(BigQueryView):
    def __init__(self, *, dataset_id: str) -> None:
        self.dataset_id = dataset_id

        # This view is the same for all customers, so we hardcode the fields.
        self.view_id = "form_submission"
        self.friendly_name = "Form Submission Event"
        self.description = "A user submitted a form."

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
            ViewField(
                definition="current_page.title",
                alias="current_page_title",
                description="The title of the page on which the form was submitted.",
                field_type=SqlTypeNames.STRING,
            ),
            ViewField(
                definition="current_page.url.path",
                alias="current_page_path",
                description="The path of the page on which the form was submitted.",
                field_type=SqlTypeNames.STRING,
            ),
            ViewField(
                definition="current_page.url.hash",
                alias="current_page_hash",
                description="The URL hash of the page on which the form was submitted.",
                field_type=SqlTypeNames.STRING,
            ),
            *_common_view_fields(),
        )

    @property
    def view_query(self) -> str:
        sanitized_fq_source_table = self.sql_sanitized_fq_table(
            table_id=BrowserEventAtom.TABLE_DEF.table_id,
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


class PageViewView(BigQueryView):
    def __init__(self, *, dataset_id: str) -> None:
        self.dataset_id = dataset_id

        # This view is the same for all customers, so we hardcode the fields.
        self.view_id = "page_view"
        self.friendly_name = "Page View Event"
        self.description = "A user navigated to a new location in their browser."

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
            ViewField(
                definition="current_page.title",
                alias="current_page_title",
                description="The title of the viewed page.",
                field_type=SqlTypeNames.STRING,
            ),
            ViewField(
                definition="current_page.url.path",
                alias="current_page_path",
                description="The path of the viewed page.",
                field_type=SqlTypeNames.STRING,
            ),
            ViewField(
                definition="current_page.url.hash",
                alias="current_page_hash",
                description="The URL hash of the viewed page.",
                field_type=SqlTypeNames.STRING,
            ),
            *_common_view_fields(),
        )

    @property
    def view_query(self) -> str:
        sanitized_fq_source_table = self.sql_sanitized_fq_table(
            table_id=BrowserEventAtom.TABLE_DEF.table_id,
        )

        sanitized_action_name = sql_sanitized_literal(BrowserAction.PAGE_VIEW)

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
