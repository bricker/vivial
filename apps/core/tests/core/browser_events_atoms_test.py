import datetime

from google.cloud.bigquery import SchemaField, SqlTypeNames

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
from eave.core.internal.atoms.db_tables import common_bq_insert_timestamp_field, common_event_timestamp_field
from eave.core.internal.atoms.payload_processors.browser_events import BrowserEventAtom, BrowserEventsTableHandle
from eave.core.internal.atoms.shared import BigQueryFieldMode
from eave.core.internal.lib.bq_client import EAVE_INTERNAL_BIGQUERY_CLIENT
from eave.core.internal.orm.team import bq_dataset_id
from eave.stdlib.logging import LogContext

from .base import assert_schemas_match
from .bq_tests_base import BigQueryTestsBase

empty_ctx = LogContext()


class TestBrowserEventsAtoms(BigQueryTestsBase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_schema(self):
        assert_schemas_match(
            BrowserEventAtom.TABLE_DEF.schema,
            (
                SchemaField(
                    name="action",
                    description="The user action that caused this event.",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                common_event_timestamp_field(),
                SessionRecordField.schema(),
                AccountRecordField.schema(),
                TrafficSourceRecordField.schema(),
                TargetRecordField.schema(),
                CurrentPageRecordField.schema(),
                DeviceRecordField.schema(),
                GeoRecordField.schema(),
                MultiScalarTypeKeyValueRecordField.schema(
                    name="extra",
                    description=self.anystr(),
                ),
                SchemaField(
                    name="client_ip",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                common_bq_insert_timestamp_field(),
            ),
        )

    async def test_insert(self) -> None:
        table = BrowserEventsTableHandle(team=self.eave_team)
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
                        self.anystr("event.extra.intkey"): self.anyint("event.extra.intval"),
                        self.anystr("event.extra.floatkey"): self.anyfloat("event.extra.floatval"),
                        self.anystr("event.extra.boolkey"): self.anybool("event.extra.boolval"),
                    },
                    "corr_ctx": {
                        "session": {
                            "id": self.anystr("event.session.id"),
                            "start_timestamp": self.anytime("event.session.start_timestamp"),
                        },
                        "traffic_source": {
                            "timestamp": self.anytime("event.traffic_source.timestamp"),
                            "browser_referrer": self.anystr("event.traffic_source.browser_referrer"),
                            "tracking_params": {
                                "gclid": self.anystr("event.traffic_source.tracking_params.gclid"),
                                "utm_campaign": self.anystr("event.traffic_source.tracking_params.utm_campaign"),
                                self.anystr("event.traffic_source.tracking_params.unrecognized.key"): self.anystr(
                                    "event.traffic_source.tracking_params.unrecognized.value"
                                ),
                            },
                        },
                        "account_id": self.anystr("event.user.account_id"),
                        "visitor_id": self.anystr("event.user.visitor_id"),
                    },
                },
            ],
            client_ip="1.2.3.4",
            geolocation=GeoRecordField(
                region="US",
                subdivision="CA",
                city="Palo Alto",
                coordinates="37.41111281622952, -122.12322865137392",
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

        assert first_row.get("action") == "CLICK"
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
            "utm_campaign": self.getstr("event.traffic_source.tracking_params.utm_campaign"),
            "other_tracking_params": [
                {
                    "key": self.anystr("event.traffic_source.tracking_params.unrecognized.key"),
                    "value": self.anystr("event.traffic_source.tracking_params.unrecognized.value"),
                },
            ],
        }

        assert first_row.get("user") == {
            "account_id": self.getstr("event.user.account_id"),
            "visitor_id": self.getstr("event.user.visitor_id"),
        }

        assert first_row.get("extra") == [
            {
                "key": self.anystr("event.extra.strkey"),
                "value": {
                    "string_value": self.anystr("event.extra.strval"),
                    "int_value": None,
                    "float_value": None,
                    "bool_value": None,
                },
            },
            {
                "key": self.anystr("event.extra.intkey"),
                "value": {
                    "string_value": None,
                    "int_value": self.anyint("event.extra.intval"),
                    "float_value": None,
                    "bool_value": None,
                },
            },
            {
                "key": self.anystr("event.extra.floatkey"),
                "value": {
                    "string_value": None,
                    "int_value": None,
                    "float_value": self.anyfloat("event.extra.floatval"),
                    "bool_value": None,
                },
            },
            {
                "key": self.anystr("event.extra.boolkey"),
                "value": {
                    "string_value": None,
                    "int_value": None,
                    "float_value": None,
                    "bool_value": self.anybool("event.extra.boolval"),
                },
            },
        ]
