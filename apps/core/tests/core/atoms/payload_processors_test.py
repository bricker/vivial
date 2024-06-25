import datetime
import json

from eave.collectors.core.correlation_context.base import EAVE_COLLECTOR_ACCOUNT_ID_ATTR_NAME, EAVE_COLLECTOR_COOKIE_PREFIX, EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX, CorrelationContextAttr
from eave.collectors.core.datastructures import DatabaseOperation, HttpRequestMethod
from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.core.internal.atoms.api_types import BrowserAction
from eave.core.internal.atoms.db_record_fields import (
    CurrentPageRecordField,
    DeviceRecordField,
    GeoRecordField,
    MultiScalarTypeKeyValueRecordField,
    SessionRecordField,
    TargetRecordField,
    TrafficSourceRecordField,
    AccountRecordField,
)
from eave.core.internal.atoms.atom_types import Atom
from eave.core.internal.atoms.payload_processors.browser_events import BrowserEventAtom, BrowserEventsTableHandle
from eave.core.internal.atoms.payload_processors.db_events import DatabaseEventsTableHandle
from eave.core.internal.atoms.payload_processors.http_server_events import HttpServerEventsTableHandle
from eave.core.internal.atoms.shared import BigQueryFieldMode
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.core.internal.orm.client_credentials import ClientCredentialsOrm, ClientScope
from eave.core.internal.orm.team import bq_dataset_id
from eave.stdlib.logging import LogContext

from eave.core.internal.orm.virtual_event import VirtualEventOrm

from ..base import assert_schemas_match
from ..bq_tests_base import BigQueryTestsBase

empty_ctx = LogContext()


class TestBrowserEventsPayloadProcessor(BigQueryTestsBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_insert(self) -> None:
        table = BrowserEventsTableHandle(team=self.eave_team, client_credentials=self.client_credentials)
        url = "https://dashboard.eave.fyi:9090/insights?q1=v1#footer"

        await table.insert_with_geolocation(
            events=[
                {
                    "action": "click",
                    "timestamp": self.anytime("event timestamp"),
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
                    "corr_ctx": {
                        f"{EAVE_COLLECTOR_COOKIE_PREFIX}visitor_id": self.anystr("event.visitor_id"),
                        f"{EAVE_COLLECTOR_COOKIE_PREFIX}session": json.dumps({
                            "id": self.anystr("event.session.id"),
                            "start_timestamp": self.anytime("event.session.start_timestamp"),
                        }),
                        f"{EAVE_COLLECTOR_COOKIE_PREFIX}traffic_source": json.dumps({
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
                        }),
                        f"{EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX}{self.anystr()}": CorrelationContextAttr(
                            key=EAVE_COLLECTOR_ACCOUNT_ID_ATTR_NAME,
                            value=self.anystr("event.account.account_id"),
                        ).to_encrypted(encryption_key=self.client_credentials.decryption_key),
                    },
                },
            ],
            client_ip=self.anystr("event.client_ip"),
            geolocation=GeoRecordField(
                region=self.anystr("event.geo.region"),
                subdivision=self.anystr("event.geo.subdivision"),
                city=self.anystr("event.geo.city"),
                coordinates=self.anystr("event.geo.coordinates"),
            ),
            ctx=empty_ctx,
        )

        assert self.bq_table_exists(table_name="atoms_browser_events")
        results = EAVE_INTERNAL_BIGQUERY_CLIENT.query(
            query=f"select * from {bq_dataset_id(self.eave_team.id)}.atoms_browser_events"
        )

        assert results.total_rows == 1
        first_row = next(results, None)
        assert first_row is not None

        assert first_row.get("action") == BrowserAction.CLICK
        assert first_row.get("timestamp") == datetime.datetime.fromtimestamp(
            self.gettime("event timestamp"), tz=datetime.UTC
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
                "domain": "dashboard.eave.fyi",
                "path": "/insights",
                "hash": "footer",
                "query_params": [
                    {
                        "key": "q1",
                        "value": "v1",
                    },
                ],
            },
            "title": self.getstr("event.current_page.title"),
            "pageview_id": self.getstr("event.current_page.pageview_id"),
        }

        assert first_row.get("session") == {
            "id": self.getstr("event.session.id"),
            "start_timestamp": datetime.datetime.fromtimestamp(
                self.gettime("event.session.start_timestamp"), tz=datetime.UTC
            ),
            "duration_ms": (self.gettime("event timestamp") - self.gettime("event.session.start_timestamp")) * 1000,
        }

        assert first_row.get("traffic_source") == {
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

        assert first_row.get("visitor_id") == self.getstr("event.visitor_id")
        assert first_row.get("account") == {
            "account_id": self.getstr("event.account.account_id"),
            "extra": [],
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
                vevent = await VirtualEventOrm.query(s, params=VirtualEventOrm.QueryParams(
                    team_id=self.eave_team.id,
                    view_id=view_id,
                ))
                assert vevent.one_or_none() is None
                assert not self.bq_table_exists(table_name=view_id)

        table = BrowserEventsTableHandle(team=self.eave_team, client_credentials=self.client_credentials)
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
            ctx=empty_ctx,
        )

        async with self.db_session.begin() as s:
            for view_id in action_names:
                vevent = await VirtualEventOrm.query(s, params=VirtualEventOrm.QueryParams(
                    team_id=self.eave_team.id,
                    view_id=view_id,
                ))
                assert vevent.one_or_none() is not None
                assert self.bq_table_exists(table_name=view_id)


class TestDatabaseEventsPayloadProcessor(BigQueryTestsBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_insert(self) -> None:
        table = DatabaseEventsTableHandle(team=self.eave_team, client_credentials=self.client_credentials)

        await table.insert(
            events=[
                {
                    "timestamp": self.anytime("event timestamp"),
                    "operation": "insert",
                    "db_name": self.anystr("event.db_name"),
                    "table_name": self.anystr("event.table_name"),
                    "statement": self.anystr("event.statement"),
                    "statement_values": {
                        self.anystr("event.statement_values.0.key"): self.anystr("event.statement_values.0.value"),
                        self.anystr("event.statement_values.1.key"): self.anyint("event.statement_values.1.value"),
                    },
                    "corr_ctx": {
                        f"{EAVE_COLLECTOR_COOKIE_PREFIX}visitor_id": self.anystr("event.visitor_id"),
                        f"{EAVE_COLLECTOR_COOKIE_PREFIX}session": json.dumps({
                            "id": self.anystr("event.session.id"),
                            "start_timestamp": self.anytime("event.session.start_timestamp"),
                        }),
                        f"{EAVE_COLLECTOR_COOKIE_PREFIX}traffic_source": json.dumps({
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
                        }),
                        f"{EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX}{self.anystr()}": CorrelationContextAttr(
                            key=EAVE_COLLECTOR_ACCOUNT_ID_ATTR_NAME,
                            value=self.anystr("event.account.account_id"),
                        ).to_encrypted(encryption_key=self.client_credentials.decryption_key),
                    },
                },
            ],
            ctx=empty_ctx,
        )

        assert self.bq_table_exists(table_name="atoms_db_events")
        results = EAVE_INTERNAL_BIGQUERY_CLIENT.query(
            query=f"select * from {bq_dataset_id(self.eave_team.id)}.atoms_db_events"
        )

        assert results.total_rows == 1
        first_row = next(results, None)
        assert first_row is not None

        assert first_row.get("operation") == DatabaseOperation.INSERT
        assert first_row.get("timestamp") == datetime.datetime.fromtimestamp(
            self.gettime("event timestamp"), tz=datetime.UTC
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

        assert first_row.get("session") == {
            "id": self.getstr("event.session.id"),
            "start_timestamp": datetime.datetime.fromtimestamp(
                self.gettime("event.session.start_timestamp"), tz=datetime.UTC
            ),
            "duration_ms": (self.gettime("event timestamp") - self.gettime("event.session.start_timestamp")) * 1000,
        }

        assert first_row.get("traffic_source") == {
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

        assert first_row.get("visitor_id") == self.getstr("event.visitor_id")
        assert first_row.get("account") == {
            "account_id": self.getstr("event.account.account_id"),
            "extra": [],
        }

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
                vevent = await VirtualEventOrm.query(s, params=VirtualEventOrm.QueryParams(
                    team_id=self.eave_team.id,
                    view_id=view_id,
                ))
                assert vevent.one_or_none() is None
                assert not self.bq_table_exists(table_name=view_id)

        table = DatabaseEventsTableHandle(team=self.eave_team, client_credentials=self.client_credentials)
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
            ctx=empty_ctx,
        )

        async with self.db_session.begin() as s:
            for view_id in expected_view_ids:
                vevent = await VirtualEventOrm.query(s, params=VirtualEventOrm.QueryParams(
                    team_id=self.eave_team.id,
                    view_id=view_id,
                ))
                assert vevent.one_or_none() is not None
                assert self.bq_table_exists(table_name=view_id)

class TestHttpServerEventsPayloadProcessor(BigQueryTestsBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_insert(self) -> None:
        table = HttpServerEventsTableHandle(team=self.eave_team, client_credentials=self.client_credentials)
        url = "https://dashboard.eave.fyi:9090/insights?q1=v1#footer"

        await table.insert(
            events=[
                {
                    "timestamp": self.anytime("event timestamp"),
                    "request_method": "post",
                    "request_url": url,
                    "request_payload": self.anyjson("event.request_payload"),
                    "request_headers": {
                        self.anystr("event.request_headers.0.key"): self.anystr("event.request_headers.0.value"),
                    },
                    "corr_ctx": {
                        f"{EAVE_COLLECTOR_COOKIE_PREFIX}visitor_id": self.anystr("event.visitor_id"),
                        f"{EAVE_COLLECTOR_COOKIE_PREFIX}session": json.dumps({
                            "id": self.anystr("event.session.id"),
                            "start_timestamp": self.anytime("event.session.start_timestamp"),
                        }),
                        f"{EAVE_COLLECTOR_COOKIE_PREFIX}traffic_source": json.dumps({
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
                        }),
                        f"{EAVE_COLLECTOR_ENCRYPTED_ACCOUNT_COOKIE_PREFIX}{self.anystr()}": CorrelationContextAttr(
                            key=EAVE_COLLECTOR_ACCOUNT_ID_ATTR_NAME,
                            value=self.anystr("event.account.account_id"),
                        ).to_encrypted(encryption_key=self.client_credentials.decryption_key),
                    },
                },
            ],
            ctx=empty_ctx,
        )

        assert self.bq_table_exists(table_name="atoms_http_server_events")
        results = EAVE_INTERNAL_BIGQUERY_CLIENT.query(
            query=f"select * from {bq_dataset_id(self.eave_team.id)}.atoms_http_server_events"
        )

        assert results.total_rows == 1
        first_row = next(results, None)
        assert first_row is not None

        assert first_row.get("request_url") == {
            "raw": url,
            "protocol": "https",
            "domain": "dashboard.eave.fyi",
            "path": "/insights",
            "hash": "footer",
            "query_params": [
                {
                    "key": "q1",
                    "value": "v1",
                },
            ],
        }

        assert first_row.get("timestamp") == datetime.datetime.fromtimestamp(
            self.gettime("event timestamp"), tz=datetime.UTC
        )

        assert first_row.get("request_payload") == self.getjson("event.request_payload")
        assert first_row.get("request_headers") == [
            {
                "key": self.getstr("event.request_headers.0.key"),
                "value": self.getstr("event.request_headers.0.value"),
            },
        ]


        assert first_row.get("session") == {
            "id": self.getstr("event.session.id"),
            "start_timestamp": datetime.datetime.fromtimestamp(
                self.gettime("event.session.start_timestamp"), tz=datetime.UTC
            ),
            "duration_ms": (self.gettime("event timestamp") - self.gettime("event.session.start_timestamp")) * 1000,
        }

        assert first_row.get("traffic_source") == {
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

        assert first_row.get("visitor_id") == self.getstr("event.visitor_id")
        assert first_row.get("account") == {
            "account_id": self.getstr("event.account.account_id"),
            "extra": [],
        }
