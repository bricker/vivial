import dataclasses
import datetime
from decimal import Decimal
import json
from textwrap import dedent
from typing import Any, cast

from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.collectors.core.correlation_context.base import (
    EAVE_COLLECTOR_ACCOUNT_ID_ATTR_NAME,
    EAVE_COLLECTOR_COOKIE_PREFIX,
    EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX,
    CorrelationContextAttr,
)
from eave.collectors.core.datastructures import DatabaseOperation
from google.cloud.bigquery import Row
from eave.core.internal.atoms.controllers.base_atom_controller import BaseAtomController
from eave.core.internal.atoms.controllers.browser_events import BrowserEventsController
from eave.core.internal.atoms.controllers.db_events import DatabaseEventsController
from eave.core.internal.atoms.controllers.http_server_events import HttpServerEventsController
from eave.core.internal.atoms.controllers.openai_chat_completion import OpenAIChatCompletionController
from eave.core.internal.atoms.models.api_payload_types import BrowserAction
from eave.core.internal.atoms.models.atom_types import Atom, BigQueryTableDefinition, OpenAIChatCompletionAtom
from eave.core.internal.atoms.models.db_record_fields import (
    GeoRecordField,
)
from eave.core.internal.atoms.models.db_views import BigQueryViewDefinition, ViewField
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.core.internal.orm.team import bq_dataset_id
from eave.core.internal.orm.virtual_event import VirtualEventOrm
from eave.stdlib.core_api.models.virtual_event import BigQueryFieldMode
from eave.stdlib.util import sql_sanitized_literal

from ..bq_tests_base import BigQueryTestsBase


class _ExampleAtom(Atom):
    @staticmethod
    def table_def() -> BigQueryTableDefinition:
        return BigQueryTableDefinition(
            table_id="atoms_example",
            friendly_name="Example Atoms",
            description="Example atoms",
            schema=(
                SchemaField(
                    name="some_field",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
            ),
        )


class _ExampleView(BigQueryViewDefinition):
    view_id = "example_view"
    friendly_name = "Example View"
    description = "example view"

    @property
    def schema(self) -> tuple[ViewField, ...]:
        return (
            ViewField(
                definition=sql_sanitized_literal("Example View"),
                alias="event_name",
                description="event name",
                field_type=SqlTypeNames.STRING,
            ),
        )

    def build_view_query(self, *, dataset_id: str) -> str:
        sanitized_fq_source_table = self.sql_sanitized_fq_table(
            dataset_id=dataset_id,
            table_id=_ExampleAtom.table_def().table_id,
        )

        return dedent(
            f"""
            SELECT
                {self.compiled_selectors}
            FROM
                {sanitized_fq_source_table}
            """
        ).strip()


class _ControllerTestBase(BigQueryTestsBase):
    _example_corr_ctx: dict[str, Any]

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        self.patch_env({
            "GAE_SERVICE": self.anystr("GAE_SERVICE"),
            "GAE_VERSION": self.anyhex("GAE_VERSION"),
            "GAE_RELEASE_DATE": self.anydatetime("GAE_RELEASE_DATE", past=True).isoformat(timespec="seconds"),
        })

        self._example_corr_ctx = {
            f"{EAVE_COLLECTOR_COOKIE_PREFIX}visitor_id": self.anystr("event.visitor_id"),
            f"{EAVE_COLLECTOR_COOKIE_PREFIX}session": json.dumps(
                {
                    "id": self.anystr("event.session.id"),
                    "start_timestamp": self.anytime("event.session.start_timestamp"),
                }
            ),
            f"{EAVE_COLLECTOR_COOKIE_PREFIX}traffic_source": json.dumps(
                {
                    "timestamp": self.anytime("event.traffic_source.timestamp"),
                    "browser_referrer": self.anystr("event.traffic_source.browser_referrer"),
                    "tracking_params": {
                        "gclid": self.anystr("event.traffic_source.tracking_params.gclid"),
                        "fbclid": self.anystr("event.traffic_source.tracking_params.fbclid"),
                        "msclkid": self.anystr("event.traffic_source.tracking_params.msclkid"),
                        "dclid": self.anystr("event.traffic_source.tracking_params.dclid"),
                        "ko_click_id": self.anystr("event.traffic_source.tracking_params.ko_click_id"),
                        "rtd_cid": self.anystr("event.traffic_source.tracking_params.rtd_cid"),
                        "li_fat_id": self.anystr("event.traffic_source.tracking_params.li_fat_id"),
                        "ttclid": self.anystr("event.traffic_source.tracking_params.ttclid"),
                        "twclid": self.anystr("event.traffic_source.tracking_params.twclid"),
                        "wbraid": self.anystr("event.traffic_source.tracking_params.wbraid"),
                        "gbraid": self.anystr("event.traffic_source.tracking_params.gbraid"),
                        "utm_campaign": self.anystr("event.traffic_source.tracking_params.utm_campaign"),
                        "utm_source": self.anystr("event.traffic_source.tracking_params.utm_source"),
                        "utm_medium": self.anystr("event.traffic_source.tracking_params.utm_medium"),
                        "utm_term": self.anystr("event.traffic_source.tracking_params.utm_term"),
                        "utm_content": self.anystr("event.traffic_source.tracking_params.utm_content"),
                        self.anystr("event.traffic_source.tracking_params.unrecognized.key"): self.anystr(
                            "event.traffic_source.tracking_params.unrecognized.value"
                        ),
                    },
                }
            ),
            f"{EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX}{self.anystr()}": CorrelationContextAttr(
                key=EAVE_COLLECTOR_ACCOUNT_ID_ATTR_NAME,
                value=self.anystr("event.account.account_id"),
            ).to_encrypted(encryption_key=self.client_credentials.decryption_key),
            f"{EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX}{self.anystr("account attr 2")}": CorrelationContextAttr(
                key=self.anyhex("event.account.extra.0.key"),
                value=self.anystr("event.account.extra.0.val"),
            ).to_encrypted(encryption_key=self.client_credentials.decryption_key),
        }

    def _corr_ctx_matches(self, row: Row) -> bool:
        assert row.get("session") == {
            "id": self.getstr("event.session.id"),
            "start_timestamp": datetime.datetime.fromtimestamp(
                self.gettime("event.session.start_timestamp"), tz=datetime.UTC
            ),
            "duration_ms": (self.gettime("event.timestamp") - self.gettime("event.session.start_timestamp")) * 1000,
        }

        assert row.get("traffic_source") == {
            "timestamp": datetime.datetime.fromtimestamp(
                self.gettime("event.traffic_source.timestamp"), tz=datetime.UTC
            ),
            "browser_referrer": self.getstr("event.traffic_source.browser_referrer"),
            "gclid": self.getstr("event.traffic_source.tracking_params.gclid"),
            "fbclid": self.getstr("event.traffic_source.tracking_params.fbclid"),
            "msclkid": self.getstr("event.traffic_source.tracking_params.msclkid"),
            "dclid": self.getstr("event.traffic_source.tracking_params.dclid"),
            "ko_click_id": self.getstr("event.traffic_source.tracking_params.ko_click_id"),
            "rtd_cid": self.getstr("event.traffic_source.tracking_params.rtd_cid"),
            "li_fat_id": self.getstr("event.traffic_source.tracking_params.li_fat_id"),
            "ttclid": self.getstr("event.traffic_source.tracking_params.ttclid"),
            "twclid": self.getstr("event.traffic_source.tracking_params.twclid"),
            "wbraid": self.getstr("event.traffic_source.tracking_params.wbraid"),
            "gbraid": self.getstr("event.traffic_source.tracking_params.gbraid"),
            "utm_campaign": self.getstr("event.traffic_source.tracking_params.utm_campaign"),
            "utm_source": self.getstr("event.traffic_source.tracking_params.utm_source"),
            "utm_medium": self.getstr("event.traffic_source.tracking_params.utm_medium"),
            "utm_term": self.getstr("event.traffic_source.tracking_params.utm_term"),
            "utm_content": self.getstr("event.traffic_source.tracking_params.utm_content"),
            "other_tracking_params": [
                {
                    "key": self.getstr("event.traffic_source.tracking_params.unrecognized.key"),
                    "value": self.getstr("event.traffic_source.tracking_params.unrecognized.value"),
                },
            ],
        }

        assert row.get("visitor_id") == self.getstr("event.visitor_id")
        assert row.get("account") == {
            "account_id": self.getstr("event.account.account_id"),
            "extra": [
                {
                    "key": self.getstr("event.account.extra.0.key"),
                    "value": {
                        "string_value": self.getstr("event.account.extra.0.val"),
                        "bool_value": None,
                        "numeric_value": None,
                    },
                }
            ],
        }

        return True

    def _bq_record_metadata_matches(self, row: Row) -> bool:
        assert row.get("metadata") == {
            "source_app_name": self.getstr("GAE_SERVICE"),
            "source_app_version": self.getstr("GAE_VERSION"),
            "source_app_release_timestamp": self.getdatetime("GAE_RELEASE_DATE").replace(microsecond=0),
        }

        insert_ts: datetime.datetime | None = row.get("metadata_insert_timestamp")
        assert insert_ts is not None

        # This 5 second grace is to account for both network latency and server/client time discrepancies.
        # Most commonly these two datetimes will be within milliseconds of each other,
        # but it's possible that there will be a larger discrepancy, even that the server timestamp will be future
        # to the client timestamp.
        # All we really want to know is that the insert timestamp is roughly correct, eg not orders of magnitude off
        # like in the case of a millisecond/second resolution mistake.
        assert datetime.datetime.now(tz=datetime.UTC) - insert_ts >= datetime.timedelta(seconds=-5)
        return True

class TestBaseAtomController(_ControllerTestBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_get_or_create_table(self):
        controller = BaseAtomController(client=self.client_credentials)
        table_def = BigQueryTableDefinition(
            table_id=self.anyhex(),
            friendly_name=self.anystr(),
            description=self.anystr(),
            schema=(
                SchemaField(
                    name=self.anyhex(),
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
            ),
        )

        assert not self.team_bq_dataset_exists()
        assert not self.team_bq_table_exists(table_name=table_def.table_id)

        # Calling this twice to test idempotency
        controller.get_or_create_bq_table(table_def=table_def, ctx=self.empty_ctx)
        controller.get_or_create_bq_table(table_def=table_def, ctx=self.empty_ctx)

        assert self.team_bq_dataset_exists()
        assert self.team_bq_table_exists(table_name=table_def.table_id)

    async def test_sync_bq_view(self):
        controller = BaseAtomController(client=self.client_credentials)
        view_def = _ExampleView()

        async with self.db_session.begin() as s:
            vevent = (
                await VirtualEventOrm.query(
                    s,
                    params=VirtualEventOrm.QueryParams(
                        team_id=self.eave_team.id,
                        view_id=view_def.view_id,
                    ),
                )
            ).one_or_none()

            assert vevent is None

        assert not self.team_bq_dataset_exists()
        assert not self.team_bq_table_exists(table_name=view_def.view_id)

        controller.get_or_create_bq_table(table_def=_ExampleAtom.table_def(), ctx=self.empty_ctx)

        # Calling this twice to test that multiple VirtualEventOrms aren't created.
        await controller.sync_bq_view(view_def=view_def, ctx=self.empty_ctx)
        await controller.sync_bq_view(view_def=view_def, ctx=self.empty_ctx)

        async with self.db_session.begin() as s:
            vevents = (
                await VirtualEventOrm.query(
                    s,
                    params=VirtualEventOrm.QueryParams(
                        team_id=self.eave_team.id,
                        view_id=view_def.view_id,
                    ),
                )
            ).all()

            assert len(vevents) == 1
            assert vevents[0].view_id == view_def.view_id

        assert self.team_bq_dataset_exists()
        assert self.team_bq_table_exists(table_name=view_def.view_id)


class TestBrowserEventsPayloadProcessor(_ControllerTestBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_insert(self) -> None:
        table = BrowserEventsController(client=self.client_credentials)
        url = f"https://{self.anyhex("url.domain")}.fyi:9090{self.anypath("url.path")}?{self.anyhex("url.qp")}={self.anyhex("url.qpv")}#{self.anyhex("url.hash")}"

        await table.insert_with_geolocation(
            events=[
                {
                    "action": "click",
                    "timestamp": self.anytime("event.timestamp"),
                    "target": {
                        "type": self.anystr("event.target.type"),
                        "id": self.anystr("event.target.id"),
                        "content": self.anystr("event.target.content"),
                        "attributes": {
                            self.anystr("event.target.attributes.0.key"): self.anystr(
                                "event.target.attributes.0.value"
                            ),
                        },
                    },
                    "device": {
                        "user_agent": self.anystr("event.device.user_agent"),
                        "brands": [
                            {
                                "brand": self.anystr("event.device.brands[0].brand"),
                                "version": self.anystr("event.device.brands[0].version"),
                            }
                        ],
                        "platform": self.anystr("event.device.platform"),
                        "platform_version": self.anystr("event.device.platform_version"),
                        "mobile": self.anybool("event.device.mobile"),
                        "form_factor": self.anystr("event.device.form_factor"),
                        "model": self.anystr("event.device.model"),
                        "screen_width": self.anyint("event.device.screen_width"),
                        "screen_height": self.anyint("event.device.screen_height"),
                        "screen_avail_width": self.anyint("event.device.screen_avail_width"),
                        "screen_avail_height": self.anyint("event.device.screen_avail_height"),
                    },
                    "current_page": {
                        "url": url,
                        "title": self.anystr("event.current_page.title"),
                        "pageview_id": self.anystr("event.current_page.pageview_id"),
                    },
                    "extra": {
                        self.anystr("event.extra.strkey"): self.anystr("event.extra.strval"),
                        self.anystr("event.extra.numerickey"): self.anyint("event.extra.numericval"),
                        self.anystr("event.extra.boolkey"): self.anybool("event.extra.boolval"),
                    },
                    "corr_ctx": self._example_corr_ctx,
                },
            ],
            client_ip=self.anystr("event.client_ip"),
            geolocation=GeoRecordField(
                region=self.anystr("event.geo.region"),
                subdivision=self.anystr("event.geo.subdivision"),
                city=self.anystr("event.geo.city"),
                coordinates=self.anystr("event.geo.coordinates"),
            ),
            ctx=self.empty_ctx,
        )

        assert self.team_bq_table_exists(table_name="atoms_browser_events")
        results = EAVE_INTERNAL_BIGQUERY_CLIENT.query(
            query=f"select * from {bq_dataset_id(self.eave_team.id)}.atoms_browser_events"
        )

        assert results.total_rows == 1
        first_row = next(results, None)
        assert first_row is not None
        assert isinstance(first_row, Row)
        assert self._corr_ctx_matches(first_row)
        assert self._bq_record_metadata_matches(first_row)

        assert first_row.get("action") == BrowserAction.CLICK
        assert first_row.get("timestamp") == datetime.datetime.fromtimestamp(
            self.gettime("event.timestamp"), tz=datetime.UTC
        )

        assert first_row.get("target") == {
            "type": self.getstr("event.target.type"),
            "id": self.getstr("event.target.id"),
            "content": self.getstr("event.target.content"),
            "attributes": [
                {
                    "key": self.getstr("event.target.attributes.0.key"),
                    "value": self.getstr("event.target.attributes.0.value"),
                }
            ],
        }

        assert first_row.get("device") == {
            "user_agent": self.getstr("event.device.user_agent"),
            "brands": [
                {
                    "brand": self.getstr("event.device.brands[0].brand"),
                    "version": self.getstr("event.device.brands[0].version"),
                }
            ],
            "platform": self.getstr("event.device.platform"),
            "platform_version": self.getstr("event.device.platform_version"),
            "mobile": self.getbool("event.device.mobile"),
            "form_factor": self.getstr("event.device.form_factor"),
            "model": self.getstr("event.device.model"),
            "screen_width": self.getint("event.device.screen_width"),
            "screen_height": self.getint("event.device.screen_height"),
            "screen_avail_width": self.getint("event.device.screen_avail_width"),
            "screen_avail_height": self.getint("event.device.screen_avail_height"),
        }

        assert first_row.get("current_page") == {
            "url": {
                "raw": url,
                "protocol": "https",
                "domain": f"{self.getstr("url.domain")}.fyi",
                "path": self.getstr("url.path"),
                "hash": self.getstr("url.hash"),
                "query_params": [
                    {
                        "key": self.getstr("url.qp"),
                        "value": self.getstr("url.qpv"),
                    },
                ],
            },
            "title": self.getstr("event.current_page.title"),
            "pageview_id": self.getstr("event.current_page.pageview_id"),
        }

        assert first_row.get("extra") == [
            {
                "key": self.getstr("event.extra.strkey"),
                "value": {
                    "string_value": self.getstr("event.extra.strval"),
                    "numeric_value": None,
                    "bool_value": None,
                },
            },
            {
                "key": self.getstr("event.extra.numerickey"),
                "value": {
                    "string_value": None,
                    "numeric_value": self.getint("event.extra.numericval"),
                    "bool_value": None,
                },
            },
            {
                "key": self.getstr("event.extra.boolkey"),
                "value": {
                    "string_value": None,
                    "numeric_value": None,
                    "bool_value": self.getbool("event.extra.boolval"),
                },
            },
        ]

    async def test_insert_view(self) -> None:
        action_names = ["click", "form_submission", "page_view"]

        async with self.db_session.begin() as s:
            for view_id in action_names:
                vevent = await VirtualEventOrm.query(
                    s,
                    params=VirtualEventOrm.QueryParams(
                        team_id=self.eave_team.id,
                        view_id=view_id,
                    ),
                )
                assert vevent.one_or_none() is None
                assert not self.team_bq_table_exists(table_name=view_id)

        table = BrowserEventsController(client=self.client_credentials)
        await table.insert_with_geolocation(
            events=[
                # Each is doubled to test that only unique views are created
                {"action": "click"},
                {"action": "click"},
                {"action": "form_submission"},
                {"action": "form_submission"},
                {"action": "page_view"},
                {"action": "page_view"},
            ],
            client_ip=None,
            geolocation=None,
            ctx=self.empty_ctx,
        )

        async with self.db_session.begin() as s:
            for view_id in action_names:
                vevent = await VirtualEventOrm.query(
                    s,
                    params=VirtualEventOrm.QueryParams(
                        team_id=self.eave_team.id,
                        view_id=view_id,
                    ),
                )
                assert vevent.one_or_none() is not None
                assert self.team_bq_table_exists(table_name=view_id)


class TestDatabaseEventsPayloadProcessor(_ControllerTestBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_insert(self) -> None:
        table = DatabaseEventsController(client=self.client_credentials)

        await table.insert(
            events=[
                {
                    "event_id": self.anyhex("event.event_id"),
                    "timestamp": self.anytime("event.timestamp"),
                    "operation": "insert",
                    "db_name": self.anystr("event.db_name"),
                    "table_name": self.anystr("event.table_name"),
                    "statement": self.anystr("event.statement"),
                    "statement_values": {
                        self.anystr("event.statement_values.0.key"): self.anystr("event.statement_values.0.value"),
                        self.anystr("event.statement_values.1.key"): self.anyint("event.statement_values.1.value"),
                    },
                    "corr_ctx": self._example_corr_ctx,
                },
            ],
            ctx=self.empty_ctx,
        )

        assert self.team_bq_table_exists(table_name="atoms_db_events")
        results = EAVE_INTERNAL_BIGQUERY_CLIENT.query(
            query=f"select * from {bq_dataset_id(self.eave_team.id)}.atoms_db_events"
        )

        assert results.total_rows == 1
        first_row = next(results, None)
        assert first_row is not None
        assert isinstance(first_row, Row)
        assert self._corr_ctx_matches(first_row)
        assert self._bq_record_metadata_matches(first_row)

        assert first_row.get("event_id") == self.getstr("event.event_id")
        assert first_row.get("operation") == DatabaseOperation.INSERT
        assert first_row.get("timestamp") == datetime.datetime.fromtimestamp(
            self.gettime("event.timestamp"), tz=datetime.UTC
        )

        assert first_row.get("db_name") == self.getstr("event.db_name")
        assert first_row.get("table_name") == self.getstr("event.table_name")
        assert first_row.get("statement") == self.getstr("event.statement")
        assert first_row.get("statement_values") == [
            {
                "key": self.getstr("event.statement_values.0.key"),
                "value": {
                    "string_value": self.getstr("event.statement_values.0.value"),
                    "numeric_value": None,
                    "bool_value": None,
                },
            },
            {
                "key": self.getstr("event.statement_values.1.key"),
                "value": {
                    "string_value": None,
                    "numeric_value": self.getint("event.statement_values.1.value"),
                    "bool_value": None,
                },
            },
        ]

    async def test_insert_view(self) -> None:
        expected_view_ids = [
            "account_created",
            "account_updated",
            "account_deleted",
            "account_queried",
            "color_created",
            "color_updated",
            "color_deleted",
            "color_queried",
        ]
        async with self.db_session.begin() as s:
            for view_id in expected_view_ids:
                vevent = await VirtualEventOrm.query(
                    s,
                    params=VirtualEventOrm.QueryParams(
                        team_id=self.eave_team.id,
                        view_id=view_id,
                    ),
                )
                assert vevent.one_or_none() is None
                assert not self.team_bq_table_exists(table_name=view_id)

        table = DatabaseEventsController(client=self.client_credentials)
        await table.insert(
            events=[
                # Some of these are doubled to test that only unique views are created
                {"operation": "insert", "table_name": "accounts"},
                {"operation": "insert", "table_name": "colors"},
                {"operation": "insert", "table_name": "colors"},
                {"operation": "update", "table_name": "accounts"},
                {"operation": "update", "table_name": "colors"},
                {"operation": "update", "table_name": "colors"},
                {"operation": "delete", "table_name": "accounts"},
                {"operation": "delete", "table_name": "colors"},
                {"operation": "delete", "table_name": "colors"},
                {"operation": "select", "table_name": "accounts"},
                {"operation": "select", "table_name": "colors"},
                {"operation": "select", "table_name": "colors"},
            ],
            ctx=self.empty_ctx,
        )

        async with self.db_session.begin() as s:
            for view_id in expected_view_ids:
                vevent = await VirtualEventOrm.query(
                    s,
                    params=VirtualEventOrm.QueryParams(
                        team_id=self.eave_team.id,
                        view_id=view_id,
                    ),
                )
                assert vevent.one_or_none() is not None
                assert self.team_bq_table_exists(table_name=view_id)


class TestOpenAIChatCompletionPayloadProcessor(_ControllerTestBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()


    async def test_insert(self) -> None:
        controller = OpenAIChatCompletionController(client=self.client_credentials)

        await controller.insert(
            events=[
                {
                    "timestamp": self.anytime("event.timestamp"),
                    "event_id": self.anyuuid("event.event_id").hex,
                    "completion_id": self.anyhex("event.completion_id"),
                    "completion_system_fingerprint": self.anyhex("event.completion_system_fingerprint"),
                    "completion_created_timestamp": self.anytime("event.completion_created_timestamp"),
                    "completion_user_id": "Bryan Ricker",
                    "service_tier": "auto",
                    "model": "gpt-4o-2024-05-13",
                    "prompt_tokens": self.anyint("event.prompt_tokens", max=1000),
                    "completion_tokens": self.anyint("event.completion_tokens", max=1000),
                    "total_tokens": self.getint("event.prompt_tokens") + self.getint("event.completion_tokens"),
                    "code_location": self.anypath("event.code_location"),
                    "openai_request": {
                        "request_params": {
                            "max_tokens": self.anyint("event.openai_request.request_params.max_tokens", max=2000),
                            "frequency_penalty": self.anyfloat("event.openai_request.request_params.frequency_penalty"),
                            "stop": self.anystr("event.openai_request.request_params.stop"),
                        },
                        "start_timestamp": self.anytime("start_timestamp"),
                        "end_timestamp": self.gettime("start_timestamp") + 5,
                        "status_code": 200,
                    },
                    "corr_ctx": self._example_corr_ctx,
                },
            ],
            ctx=self.empty_ctx,
        )

        assert self.team_bq_table_exists(table_name="atoms_openai_chat_completions")
        results = EAVE_INTERNAL_BIGQUERY_CLIENT.query(
            query=f"select * from {bq_dataset_id(self.eave_team.id)}.atoms_openai_chat_completions"
        )

        assert results.total_rows == 1
        first_row = next(results, None)
        assert first_row is not None
        assert isinstance(first_row, Row)
        assert self._corr_ctx_matches(first_row)
        assert self._bq_record_metadata_matches(first_row)

        assert first_row.get("event_id") == self.getuuid("event.event_id").hex
        assert first_row.get("timestamp") == datetime.datetime.fromtimestamp(
            self.gettime("event.timestamp"), tz=datetime.UTC
        )

        assert first_row.get("completion_id") == self.gethex("event.completion_id")
        assert first_row.get("completion_system_fingerprint") == self.gethex("event.completion_system_fingerprint")
        assert cast(datetime.datetime, first_row.get("completion_created_timestamp")).timestamp() == self.gettime("event.completion_created_timestamp")
        assert first_row.get("completion_user_id") == "Bryan Ricker"
        assert first_row.get("service_tier") == "auto"
        assert first_row.get("model") == "gpt-4o-2024-05-13"
        assert first_row.get("prompt_tokens") == self.getint("event.prompt_tokens")
        assert first_row.get("completion_tokens") == self.getint("event.completion_tokens")
        assert first_row.get("total_tokens") == self.getint("event.prompt_tokens") + self.getint("event.completion_tokens")
        assert first_row.get("code_location") == self.getpath("event.code_location")

        # Just assert that some data was inserted. We'll test the actual costs later.
        assert first_row.get("input_cost_usd_cents") is not None
        assert first_row.get("output_cost_usd_cents") is not None
        assert first_row.get("total_cost_usd_cents") is not None

        assert first_row.get("openai_request") == {
            "request_params": [
                {
                    "key": "max_tokens",
                    "value": {
                        "numeric_value": Decimal(str(self.getint("event.openai_request.request_params.max_tokens"))),
                        "string_value": None,
                        "bool_value": None,
                    },
                },
                {
                    "key": "frequency_penalty",
                    "value": {
                        "numeric_value": Decimal(str(self.getfloat("event.openai_request.request_params.frequency_penalty"))),
                        "string_value": None,
                        "bool_value": None,
                    },
                },
                {
                    "key": "stop",
                    "value": {
                        "numeric_value": None,
                        "string_value": self.getstr("event.openai_request.request_params.stop"),
                        "bool_value": None,
                    },
                },
            ],
            "start_timestamp": datetime.datetime.fromtimestamp(self.gettime("start_timestamp"), tz=datetime.UTC),
            "end_timestamp": datetime.datetime.fromtimestamp(self.gettime("start_timestamp") + 5, tz=datetime.UTC),
            "duration_ms": 5000, # 5 seconds, hardcoded in this test (start_timestamp + 5)
            "status_code": 200,
        }

    async def test_costs(self) -> None:
        controller = OpenAIChatCompletionController(client=self.client_credentials)

        await controller.insert(
            events=[
                {
                    "model": "gpt-4o-2024-05-13",
                    "prompt_tokens": 100,
                    "completion_tokens": 1000,
                    "total_tokens": 1100,
                },
            ],
            ctx=self.empty_ctx,
        )

        results = EAVE_INTERNAL_BIGQUERY_CLIENT.query(
            query=f"select * from {bq_dataset_id(self.eave_team.id)}.atoms_openai_chat_completions"
        )

        assert results.total_rows == 1
        first_row = next(results, None)
        assert first_row is not None
        assert isinstance(first_row, Row)

        # These values are based on the passed-in model and token counts. See the OpenAI Pricing module for the calculations.
        assert first_row.get("input_cost_usd_cents") == Decimal("0.05")
        assert first_row.get("output_cost_usd_cents") == Decimal("1.5")
        assert first_row.get("total_cost_usd_cents") == Decimal("1.55")



class TestHttpServerEventsPayloadProcessor(_ControllerTestBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_insert(self) -> None:
        table = HttpServerEventsController(client=self.client_credentials)
        url = f"https://{self.anyhex("url.domain")}.fyi:9090{self.anypath("url.path")}?{self.anyhex("url.qp")}={self.anyhex("url.qpv")}#{self.anyhex("url.hash")}"

        await table.insert(
            events=[
                {
                    "timestamp": self.anytime("event.timestamp"),
                    "request_method": "post",
                    "request_url": url,
                    "request_payload": self.anyjson("event.request_payload"),
                    "request_headers": {
                        self.anystr("event.request_headers.0.key"): self.anystr("event.request_headers.0.value"),
                    },
                    "corr_ctx": self._example_corr_ctx,
                },
            ],
            ctx=self.empty_ctx,
        )

        assert self.team_bq_table_exists(table_name="atoms_http_server_events")
        results = EAVE_INTERNAL_BIGQUERY_CLIENT.query(
            query=f"select * from {bq_dataset_id(self.eave_team.id)}.atoms_http_server_events"
        )

        assert results.total_rows == 1
        first_row = next(results, None)
        assert first_row is not None
        assert isinstance(first_row, Row)
        assert self._corr_ctx_matches(first_row)
        assert self._bq_record_metadata_matches(first_row)

        assert first_row.get("request_url") == {
            "raw": url,
            "protocol": "https",
            "domain": f"{self.getstr("url.domain")}.fyi",
            "path": self.getpath("url.path"),
            "hash": self.getstr("url.hash"),
            "query_params": [
                {
                    "key": self.getstr("url.qp"),
                    "value": self.getstr("url.qpv"),
                },
            ],
        }

        assert first_row.get("timestamp") == datetime.datetime.fromtimestamp(
            self.gettime("event.timestamp"), tz=datetime.UTC
        )

        assert first_row.get("request_payload") == self.getjson("event.request_payload")
        assert first_row.get("request_headers") == [
            {
                "key": self.getstr("event.request_headers.0.key"),
                "value": self.getstr("event.request_headers.0.value"),
            },
        ]
