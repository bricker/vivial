import dataclasses
from decimal import Decimal

from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.core.internal.atoms.models.api_payload_types import (
    AccountProperties,
    CurrentPageProperties,
    DeviceBrandProperties,
    DeviceProperties,
    SessionProperties,
    TargetProperties,
    TrafficSourceProperties,
)
from eave.core.internal.atoms.models.db_record_fields import (
    AccountRecordField,
    BrandsRecordField,
    CurrentPageRecordField,
    DeviceRecordField,
    GeoRecordField,
    MetadataRecordField,
    MultiScalarTypeKeyValueRecordField,
    Numeric,
    OpenAIRequestPropertiesRecordField,
    SessionRecordField,
    SingleScalarTypeKeyValueRecordField,
    TargetRecordField,
    TrafficSourceRecordField,
    TypedValueRecordField,
    UrlRecordField,
)
from eave.stdlib.core_api.models.virtual_event import BigQueryFieldMode
from eave.stdlib.typing import JsonScalar

from ..base import BaseTestCase, assert_schemas_match


class TestTypedValueRecordField(BaseTestCase):
    async def test_schema(self) -> None:
        assert_schemas_match(
            (TypedValueRecordField.schema(),),
            (
                SchemaField(
                    name="value",
                    field_type=SqlTypeNames.RECORD,
                    mode=BigQueryFieldMode.NULLABLE,
                    fields=(
                        SchemaField(
                            name="string_value",
                            field_type=SqlTypeNames.STRING,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        SchemaField(
                            name="numeric_value",
                            field_type=SqlTypeNames.NUMERIC,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        SchemaField(
                            name="bool_value",
                            field_type=SqlTypeNames.BOOLEAN,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                    ),
                ),
            ),
        )


class TestMultiTypeKeyValueRecordField(BaseTestCase):
    async def test_schema(self) -> None:
        assert_schemas_match(
            (MultiScalarTypeKeyValueRecordField.schema(name=self.anystr("record"), description=self.anystr()),),
            (
                SchemaField(
                    name=self.getstr("record"),
                    field_type=SqlTypeNames.RECORD,
                    mode=BigQueryFieldMode.REPEATED,
                    fields=(
                        SchemaField(
                            name="key",
                            field_type=SqlTypeNames.STRING,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        TypedValueRecordField.schema(),
                    ),
                ),
            ),
        )

    async def test_field(self) -> None:
        e = MultiScalarTypeKeyValueRecordField.list_from_scalar_dict(
            {
                self.anystr("key for str"): self.anystr("str value"),
                self.anystr("key for numeric"): self.anyfloat("numeric value"),
                self.anystr("key for bool"): self.anybool("bool value"),
                self.anystr("key for None"): None,
            }
        )

        assert len(e) == 4
        assert e[0].key == self.getstr("key for str")
        assert e[0].value is not None
        assert e[0].value.string_value == self.getstr("str value")
        assert e[0].value.numeric_value is None
        assert e[0].value.bool_value is None

        assert e[1].key == self.getstr("key for numeric")
        assert e[1].value is not None
        assert e[1].value.string_value is None
        assert e[1].value.numeric_value == Numeric(self.getfloat("numeric value"))
        assert e[1].value.bool_value is None

        assert e[2].key == self.getstr("key for bool")
        assert e[2].value is not None
        assert e[2].value.string_value is None
        assert e[2].value.numeric_value is None
        assert e[2].value.bool_value == self.getbool("bool value")

        assert e[3].key == self.getstr("key for None")
        assert e[3].value is not None
        assert e[3].value.string_value is None
        assert e[3].value.numeric_value is None
        assert e[3].value.bool_value is None

        assert dataclasses.asdict(e[1]) == {
            "key": self.getstr("key for numeric"),
            "value": {
                "string_value": None,
                "numeric_value": str(self.getfloat("numeric value")),
                "bool_value": None,
            },
        }


class TestSingleScalarTypeKeyValueRecordField(BaseTestCase):
    async def test_schema(self) -> None:
        assert_schemas_match(
            (
                SingleScalarTypeKeyValueRecordField.schema(
                    name=self.anystr("record"),
                    description=self.anystr(),
                    value_type=SqlTypeNames.INTEGER,
                ),
            ),
            (
                SchemaField(
                    name=self.getstr("record"),
                    field_type=SqlTypeNames.RECORD,
                    mode=BigQueryFieldMode.REPEATED,
                    fields=(
                        SchemaField(
                            name="key",
                            field_type=SqlTypeNames.STRING,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        SchemaField(
                            name="value",
                            field_type=SqlTypeNames.INTEGER,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                    ),
                ),
            ),
        )

    async def test_field(self) -> None:
        e = SingleScalarTypeKeyValueRecordField.list_from_scalar_dict(
            {
                self.anystr("key for int"): self.anyint("int value"),
                self.anystr("key for None"): None,
            }
        )

        assert len(e) == 2

        assert e[0].key == self.getstr("key for int")
        assert e[0].value == self.getint("int value")

        assert e[1].key == self.getstr("key for None")
        assert e[1].value is None

        assert dataclasses.asdict(e[0]) == {
            "key": self.getstr("key for int"),
            "value": self.getint("int value"),
        }

        assert dataclasses.asdict(e[1]) == {
            "key": self.getstr("key for None"),
            "value": None,
        }


class TestSessionRecordField(BaseTestCase):
    async def test_schema(self) -> None:
        # idk... is this test useful? It's important that the schemas don't accidentally change.
        # But defining every schema twice (once in tests, once in source) sounds horrible.
        assert_schemas_match(
            (SessionRecordField.schema(),),
            (
                SchemaField(
                    name="session",
                    field_type=SqlTypeNames.RECORD,
                    mode=BigQueryFieldMode.NULLABLE,
                    fields=(
                        SchemaField(
                            name="id",
                            field_type=SqlTypeNames.STRING,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        SchemaField(
                            name="start_timestamp",
                            field_type=SqlTypeNames.TIMESTAMP,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        SchemaField(
                            name="duration_ms",
                            field_type=SqlTypeNames.FLOAT,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                    ),
                ),
            ),
        )

    async def test_field(self) -> None:
        start_timestamp_sec = self.anytime()
        event_timestamp_sec = start_timestamp_sec + 60  # + 1 minute
        expected_duration_ms = 60 * 1000

        e = SessionRecordField.from_api_resource(
            resource=SessionProperties(
                id=self.anystr("session.id"),
                start_timestamp=start_timestamp_sec,
            ),
            event_timestamp=event_timestamp_sec,
        )
        assert e is not None
        assert e.id == self.getstr("session.id")
        assert e.start_timestamp == start_timestamp_sec
        assert e.duration_ms == expected_duration_ms

        assert dataclasses.asdict(e) == {
            "id": self.getstr("session.id"),
            "start_timestamp": start_timestamp_sec,
            "duration_ms": expected_duration_ms,
        }

    async def test_field_no_values(self) -> None:
        e = SessionRecordField.from_api_resource(
            resource=SessionProperties(
                id=None,
                start_timestamp=None,
            ),
            event_timestamp=None,
        )
        assert e is not None
        assert e.id is None
        assert e.start_timestamp is None
        assert e.duration_ms is None

    async def test_field_no_timestamp(self) -> None:
        e = SessionRecordField.from_api_resource(
            resource=SessionProperties(
                id=self.anystr("session.id"),
                start_timestamp=self.anytime("session.start_timestamp"),
            ),
            event_timestamp=None,
        )
        assert e is not None
        assert e.id == self.getstr("session.id")
        assert e.start_timestamp == self.getstr("session.start_timestamp")
        assert e.duration_ms is None


class TestAccountRecordField(BaseTestCase):
    async def test_schema(self) -> None:
        assert_schemas_match(
            (AccountRecordField.schema(),),
            (
                SchemaField(
                    name="account",
                    field_type=SqlTypeNames.RECORD,
                    mode=BigQueryFieldMode.NULLABLE,
                    fields=(
                        SchemaField(
                            name="account_id",
                            field_type=SqlTypeNames.STRING,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        MultiScalarTypeKeyValueRecordField.schema(
                            name="extra",
                            description=self.anystr(),
                        ),
                    ),
                ),
            ),
        )

    async def test_field(self) -> None:
        extra: dict[str, JsonScalar] = {self.anystr("k1"): self.anystr("v1")}
        e = AccountRecordField.from_api_resource(
            resource=AccountProperties(
                account_id=self.anystr("account.account_id"),
                extra=extra,
            ),
        )

        assert e.account_id == self.getstr("account.account_id")
        assert e.extra is not None
        assert e.extra == MultiScalarTypeKeyValueRecordField.list_from_scalar_dict(extra)

        assert dataclasses.asdict(e) == {
            "account_id": self.getstr("account.account_id"),
            "extra": [dataclasses.asdict(x) for x in e.extra],
        }


class TestTrafficSourceRecordField(BaseTestCase):
    async def test_schema(self) -> None:
        expected_tracking_params = [
            "browser_referrer",
            "gclid",
            "fbclid",
            "msclkid",
            "dclid",
            "ko_click_id",
            "rtd_cid",
            "li_fat_id",
            "ttclid",
            "twclid",
            "wbraid",
            "gbraid",
            "utm_campaign",
            "utm_source",
            "utm_medium",
            "utm_term",
            "utm_content",
        ]

        assert_schemas_match(
            (TrafficSourceRecordField.schema(),),
            (
                SchemaField(
                    name="traffic_source",
                    field_type=SqlTypeNames.RECORD,
                    mode=BigQueryFieldMode.NULLABLE,
                    fields=(
                        SchemaField(
                            name="timestamp",
                            field_type=SqlTypeNames.TIMESTAMP,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        *[
                            SchemaField(
                                name=k,
                                field_type=SqlTypeNames.STRING,
                                mode=BigQueryFieldMode.NULLABLE,
                            )
                            for k in expected_tracking_params
                        ],
                        SingleScalarTypeKeyValueRecordField.schema(
                            name="other_tracking_params",
                            description=self.anystr(),
                            value_type=SqlTypeNames.STRING,
                        ),
                    ),
                ),
            ),
        )

    async def test_field(self) -> None:
        e = TrafficSourceRecordField.from_api_resource(
            resource=TrafficSourceProperties(
                timestamp=self.anytime("traffic_source.timestamp"),
                browser_referrer=self.anystr("traffic_source.browser_referrer"),
                tracking_params={
                    "gclid": self.anystr("traffic_source.tracking_params.gclid"),
                    "fbclid": self.anystr("traffic_source.tracking_params.fbclid"),
                    "msclkid": self.anystr("traffic_source.tracking_params.msclkid"),
                    "dclid": self.anystr("traffic_source.tracking_params.dclid"),
                    "ko_click_id": self.anystr("traffic_source.tracking_params.ko_click_id"),
                    "rtd_cid": self.anystr("traffic_source.tracking_params.rtd_cid"),
                    "li_fat_id": self.anystr("traffic_source.tracking_params.li_fat_id"),
                    "ttclid": self.anystr("traffic_source.tracking_params.ttclid"),
                    "twclid": self.anystr("traffic_source.tracking_params.twclid"),
                    "wbraid": self.anystr("traffic_source.tracking_params.wbraid"),
                    "gbraid": self.anystr("traffic_source.tracking_params.gbraid"),
                    "utm_campaign": self.anystr("traffic_source.tracking_params.utm_campaign"),
                    "utm_source": self.anystr("traffic_source.tracking_params.utm_source"),
                    "utm_medium": self.anystr("traffic_source.tracking_params.utm_medium"),
                    "utm_term": self.anystr("traffic_source.tracking_params.utm_term"),
                    "utm_content": self.anystr("traffic_source.tracking_params.utm_content"),
                    self.anystr("extra tracking param key"): self.anystr("extra tracking param value"),
                },
            )
        )
        assert e is not None
        assert e.timestamp == self.gettime("traffic_source.timestamp")
        assert e.browser_referrer == self.getstr("traffic_source.browser_referrer")
        assert e.gclid == self.getstr("traffic_source.tracking_params.gclid")
        assert e.fbclid == self.getstr("traffic_source.tracking_params.fbclid")
        assert e.msclkid == self.getstr("traffic_source.tracking_params.msclkid")
        assert e.dclid == self.getstr("traffic_source.tracking_params.dclid")
        assert e.ko_click_id == self.getstr("traffic_source.tracking_params.ko_click_id")
        assert e.rtd_cid == self.getstr("traffic_source.tracking_params.rtd_cid")
        assert e.li_fat_id == self.getstr("traffic_source.tracking_params.li_fat_id")
        assert e.ttclid == self.getstr("traffic_source.tracking_params.ttclid")
        assert e.twclid == self.getstr("traffic_source.tracking_params.twclid")
        assert e.wbraid == self.getstr("traffic_source.tracking_params.wbraid")
        assert e.gbraid == self.getstr("traffic_source.tracking_params.gbraid")
        assert e.utm_campaign == self.getstr("traffic_source.tracking_params.utm_campaign")
        assert e.utm_source == self.getstr("traffic_source.tracking_params.utm_source")
        assert e.utm_medium == self.getstr("traffic_source.tracking_params.utm_medium")
        assert e.utm_term == self.getstr("traffic_source.tracking_params.utm_term")
        assert e.utm_content == self.getstr("traffic_source.tracking_params.utm_content")
        assert e.other_tracking_params == SingleScalarTypeKeyValueRecordField[str].list_from_scalar_dict(
            {
                self.getstr("extra tracking param key"): self.getstr("extra tracking param value"),
            }
        )

        assert dataclasses.asdict(e) == {
            "timestamp": self.gettime("traffic_source.timestamp"),
            "browser_referrer": self.getstr("traffic_source.browser_referrer"),
            "gclid": self.getstr("traffic_source.tracking_params.gclid"),
            "fbclid": self.getstr("traffic_source.tracking_params.fbclid"),
            "msclkid": self.getstr("traffic_source.tracking_params.msclkid"),
            "dclid": self.getstr("traffic_source.tracking_params.dclid"),
            "ko_click_id": self.getstr("traffic_source.tracking_params.ko_click_id"),
            "rtd_cid": self.getstr("traffic_source.tracking_params.rtd_cid"),
            "li_fat_id": self.getstr("traffic_source.tracking_params.li_fat_id"),
            "ttclid": self.getstr("traffic_source.tracking_params.ttclid"),
            "twclid": self.getstr("traffic_source.tracking_params.twclid"),
            "wbraid": self.getstr("traffic_source.tracking_params.wbraid"),
            "gbraid": self.getstr("traffic_source.tracking_params.gbraid"),
            "utm_campaign": self.getstr("traffic_source.tracking_params.utm_campaign"),
            "utm_source": self.getstr("traffic_source.tracking_params.utm_source"),
            "utm_medium": self.getstr("traffic_source.tracking_params.utm_medium"),
            "utm_term": self.getstr("traffic_source.tracking_params.utm_term"),
            "utm_content": self.getstr("traffic_source.tracking_params.utm_content"),
            "other_tracking_params": [
                {
                    "key": self.getstr("extra tracking param key"),
                    "value": self.getstr("extra tracking param value"),
                },
            ],
        }

    async def test_field_no_values(self) -> None:
        e = TrafficSourceRecordField.from_api_resource(
            resource=TrafficSourceProperties(
                timestamp=None,
                browser_referrer=None,
                tracking_params=None,
            )
        )
        assert e is not None
        assert e.timestamp is None
        assert e.browser_referrer is None
        assert e.gclid is None  # etc. for other tracking params


class TestGeoRecordField(BaseTestCase):
    async def test_schema(self) -> None:
        expected_fields = [
            "region",
            "subdivision",
            "city",
            "coordinates",
        ]

        assert_schemas_match(
            (GeoRecordField.schema(),),
            (
                SchemaField(
                    name="geo",
                    field_type=SqlTypeNames.RECORD,
                    mode=BigQueryFieldMode.NULLABLE,
                    fields=(
                        *[
                            SchemaField(
                                name=k,
                                field_type=SqlTypeNames.STRING,
                                mode=BigQueryFieldMode.NULLABLE,
                            )
                            for k in expected_fields
                        ],
                    ),
                ),
            ),
        )

    async def test_field(self) -> None:
        e = GeoRecordField(
            region=self.anystr("geo.region"),
            subdivision=self.anystr("geo.subdivision"),
            city=self.anystr("geo.city"),
            coordinates=self.anystr("geo.coordinates"),
        )

        assert e.region == self.getstr("geo.region")
        assert e.subdivision == self.getstr("geo.subdivision")
        assert e.city == self.getstr("geo.city")
        assert e.coordinates == self.getstr("geo.coordinates")

        assert dataclasses.asdict(e) == {
            "region": self.getstr("geo.region"),
            "subdivision": self.getstr("geo.subdivision"),
            "city": self.getstr("geo.city"),
            "coordinates": self.getstr("geo.coordinates"),
        }


class TestBrandsRecordField(BaseTestCase):
    async def test_schema(self) -> None:
        expected_fields = [
            "brand",
            "version",
        ]

        assert_schemas_match(
            (BrandsRecordField.schema(),),
            (
                SchemaField(
                    name="brands",
                    field_type=SqlTypeNames.RECORD,
                    mode=BigQueryFieldMode.REPEATED,
                    fields=(
                        *[
                            SchemaField(
                                name=k,
                                field_type=SqlTypeNames.STRING,
                                mode=BigQueryFieldMode.NULLABLE,
                            )
                            for k in expected_fields
                        ],
                    ),
                ),
            ),
        )

    async def test_field(self) -> None:
        e = BrandsRecordField.from_api_resource(
            resource=DeviceBrandProperties(
                brand=self.anystr("brand.brand"),
                version=self.anystr("brand.version"),
            ),
        )
        assert e is not None
        assert e.brand == self.getstr("brand.brand")
        assert e.version == self.getstr("brand.version")

        assert dataclasses.asdict(e) == {
            "brand": self.getstr("brand.brand"),
            "version": self.getstr("brand.version"),
        }

    async def test_field_no_values(self) -> None:
        e = BrandsRecordField.from_api_resource(
            resource=DeviceBrandProperties(
                brand=None,
                version=None,
            ),
        )
        assert e is not None
        assert e.brand is None
        assert e.version is None


class TestDeviceRecordField(BaseTestCase):
    async def test_schema(self) -> None:
        assert_schemas_match(
            (DeviceRecordField.schema(),),
            (
                SchemaField(
                    name="device",
                    field_type=SqlTypeNames.RECORD,
                    mode=BigQueryFieldMode.NULLABLE,
                    fields=(
                        SchemaField(
                            name="user_agent",
                            field_type=SqlTypeNames.STRING,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        BrandsRecordField.schema(),
                        SchemaField(
                            name="platform",
                            field_type=SqlTypeNames.STRING,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        SchemaField(
                            name="platform_version",
                            field_type=SqlTypeNames.STRING,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        SchemaField(
                            name="mobile",
                            field_type=SqlTypeNames.BOOLEAN,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        SchemaField(
                            name="form_factor",
                            field_type=SqlTypeNames.STRING,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        SchemaField(
                            name="model",
                            field_type=SqlTypeNames.STRING,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        SchemaField(
                            name="screen_width",
                            field_type=SqlTypeNames.INTEGER,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        SchemaField(
                            name="screen_height",
                            field_type=SqlTypeNames.INTEGER,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        SchemaField(
                            name="screen_avail_width",
                            field_type=SqlTypeNames.INTEGER,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        SchemaField(
                            name="screen_avail_height",
                            field_type=SqlTypeNames.INTEGER,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                    ),
                ),
            ),
        )

    async def test_field(self) -> None:
        e = DeviceRecordField.from_api_resource(
            resource=DeviceProperties(
                user_agent=self.anystr("device.user_agent"),
                brands=[
                    DeviceBrandProperties(
                        brand=self.anystr("device.brands[0].brand"),
                        version=self.anystr("device.brands[0].version"),
                    )
                ],
                platform=self.anystr("device.platform"),
                mobile=self.anybool("device.mobile"),
                form_factor=self.anystr("device.form_factor"),
                model=self.anystr("device.model"),
                platform_version=self.anystr("device.platform_version"),
                screen_width=self.anyint("device.screen_width"),
                screen_height=self.anyint("device.screen_height"),
                screen_avail_width=self.anyint("device.screen_avail_width"),
                screen_avail_height=self.anyint("device.screen_avail_height"),
            ),
        )
        assert e is not None
        assert e.user_agent == self.getstr("device.user_agent")
        assert e.brands is not None
        assert len(e.brands) == 1
        assert e.brands[0].brand == self.getstr("device.brands[0].brand")
        assert e.brands[0].version == self.getstr("device.brands[0].version")
        assert e.platform == self.getstr("device.platform")
        assert e.mobile == self.getbool("device.mobile")
        assert e.form_factor == self.getstr("device.form_factor")
        assert e.model == self.getstr("device.model")
        assert e.platform_version == self.getstr("device.platform_version")
        assert e.screen_width == self.getint("device.screen_width")
        assert e.screen_height == self.getint("device.screen_height")
        assert e.screen_avail_width == self.getint("device.screen_avail_width")
        assert e.screen_avail_height == self.getint("device.screen_avail_height")

        assert dataclasses.asdict(e) == {
            "user_agent": self.getstr("device.user_agent"),
            "brands": [
                {
                    "brand": self.getstr("device.brands[0].brand"),
                    "version": self.getstr("device.brands[0].version"),
                }
            ],
            "platform": self.getstr("device.platform"),
            "mobile": self.getbool("device.mobile"),
            "form_factor": self.getstr("device.form_factor"),
            "model": self.getstr("device.model"),
            "platform_version": self.getstr("device.platform_version"),
            "screen_width": self.getint("device.screen_width"),
            "screen_height": self.getint("device.screen_height"),
            "screen_avail_width": self.getint("device.screen_avail_width"),
            "screen_avail_height": self.getint("device.screen_avail_height"),
        }

    async def test_field_no_values(self) -> None:
        e = DeviceRecordField.from_api_resource(
            resource=DeviceProperties(
                user_agent=None,
                brands=None,
                platform=None,
                mobile=None,
                form_factor=None,
                model=None,
                platform_version=None,
                screen_width=None,
                screen_height=None,
                screen_avail_width=None,
                screen_avail_height=None,
            ),
        )
        assert e is not None
        assert e.user_agent is None
        assert e.brands is None
        assert e.platform is None
        assert e.mobile is None
        assert e.form_factor is None
        assert e.model is None
        assert e.platform_version is None
        assert e.screen_width is None
        assert e.screen_height is None
        assert e.screen_avail_width is None
        assert e.screen_avail_height is None


class TestTargetRecordField(BaseTestCase):
    async def test_schema(self) -> None:
        expected_fields = [
            "type",
            "id",
            "content",
        ]

        assert_schemas_match(
            (TargetRecordField.schema(),),
            (
                SchemaField(
                    name="target",
                    field_type=SqlTypeNames.RECORD,
                    mode=BigQueryFieldMode.NULLABLE,
                    fields=(
                        *[
                            SchemaField(
                                name=k,
                                field_type=SqlTypeNames.STRING,
                                mode=BigQueryFieldMode.NULLABLE,
                            )
                            for k in expected_fields
                        ],
                        SingleScalarTypeKeyValueRecordField.schema(
                            name="attributes",
                            description=self.anystr(),
                            value_type=SqlTypeNames.STRING,
                        ),
                    ),
                ),
            ),
        )

    async def test_field(self) -> None:
        attrs: dict[str, str | None] = {
            self.anystr("attributes[0].key"): self.anystr("attributes[0].value"),
            self.anystr("attributes[1].key"): self.anystr("attributes[1].value"),
        }

        e = TargetRecordField.from_api_resource(
            resource=TargetProperties(
                type=self.anystr("target.type"),
                id=self.anystr("target.id"),
                content=self.anystr("target.content"),
                attributes=attrs,
            ),
        )
        assert e is not None
        assert e.type == self.getstr("target.type")
        assert e.id == self.getstr("target.id")
        assert e.content == self.getstr("target.content")
        assert e.attributes == SingleScalarTypeKeyValueRecordField[str].list_from_scalar_dict(attrs)

        assert dataclasses.asdict(e) == {
            "type": self.getstr("target.type"),
            "id": self.getstr("target.id"),
            "content": self.getstr("target.content"),
            "attributes": [
                {
                    "key": self.getstr("attributes[0].key"),
                    "value": self.getstr("attributes[0].value"),
                },
                {
                    "key": self.getstr("attributes[1].key"),
                    "value": self.getstr("attributes[1].value"),
                },
            ],
        }

    async def test_field_no_values(self) -> None:
        e = TargetRecordField.from_api_resource(
            resource=TargetProperties(
                type=None,
                id=None,
                content=None,
                attributes=None,
            ),
        )
        assert e is not None
        assert e.type is None
        assert e.id is None
        assert e.content is None
        assert e.attributes is None


class TestUrlRecordField(BaseTestCase):
    async def test_schema(self) -> None:
        expected_fields = [
            "raw",
            "protocol",
            "domain",
            "path",
            "hash",
        ]

        assert_schemas_match(
            (UrlRecordField.schema(name="url", description=self.anystr()),),
            (
                SchemaField(
                    name="url",
                    field_type=SqlTypeNames.RECORD,
                    mode=BigQueryFieldMode.NULLABLE,
                    fields=(
                        *[
                            SchemaField(
                                name=k,
                                field_type=SqlTypeNames.STRING,
                                mode=BigQueryFieldMode.NULLABLE,
                            )
                            for k in expected_fields
                        ],
                        SingleScalarTypeKeyValueRecordField.schema(
                            name="query_params",
                            description=self.anystr(),
                            value_type=SqlTypeNames.STRING,
                        ),
                    ),
                ),
            ),
        )

    async def test_field(self) -> None:
        url = "".join(
            (
                f"https://{self.anyhex("url.domain")}.fyi:8080",
                f"{self.anypath("url.path")}",
                f"?{self.anyhex("url.qp.k1")}={self.anyhex("url.qp.v1")}",
                f"&{self.gethex("url.qp.k1")}={self.anyhex("url.qp.v1-2")}",
                f"&{self.anyhex("url.qp.k2")}={self.anyhex("url.qp.v2")}",
                f"&{self.anyhex("url.qp.k3")}",
                f"#{self.anyhex("url.hash")}",
            )
        )

        e = UrlRecordField.from_api_resource(resource=url)
        assert e is not None
        assert e.raw == url
        assert e.protocol == "https"
        assert e.domain == f"{self.getstr("url.domain")}.fyi"
        assert e.path == self.getstr("url.path")
        assert e.hash == self.getstr("url.hash")
        assert e.query_params == SingleScalarTypeKeyValueRecordField[str].list_from_kv_tuples(
            [
                (self.gethex("url.qp.k1"), self.gethex("url.qp.v1")),
                (self.gethex("url.qp.k1"), self.gethex("url.qp.v1-2")),
                (self.gethex("url.qp.k2"), self.gethex("url.qp.v2")),
                (self.gethex("url.qp.k3"), ""),
            ]
        )

        assert dataclasses.asdict(e) == {
            "raw": url,
            "protocol": "https",
            "domain": f"{self.getstr("url.domain")}.fyi",
            "path": self.getstr("url.path"),
            "hash": self.getstr("url.hash"),
            "query_params": [
                {
                    "key": self.gethex("url.qp.k1"),
                    "value": self.gethex("url.qp.v1"),
                },
                {
                    "key": self.gethex("url.qp.k1"),
                    "value": self.gethex("url.qp.v1-2"),
                },
                {
                    "key": self.gethex("url.qp.k2"),
                    "value": self.gethex("url.qp.v2"),
                },
                {
                    "key": self.gethex("url.qp.k3"),
                    "value": "",
                },
            ],
        }

    async def test_field_no_query(self) -> None:
        e = UrlRecordField.from_api_resource(resource="https://dashboard.eave.fyi/insights/abc")
        assert e is not None
        assert e.query_params is None

    async def test_field_no_fragment(self) -> None:
        e = UrlRecordField.from_api_resource(resource="https://dashboard.eave.fyi/insights/abc?q1=v1")
        assert e is not None
        assert e.hash is None

    async def test_field_no_path(self) -> None:
        e = UrlRecordField.from_api_resource(resource="https://dashboard.eave.fyi")
        assert e is not None
        assert e.path is None

    async def test_field_path_trailing_slash(self) -> None:
        e = UrlRecordField.from_api_resource(resource="https://dashboard.eave.fyi/")
        assert e is not None
        assert e.path is None

        e = UrlRecordField.from_api_resource(resource="https://dashboard.eave.fyi/insights/")
        assert e is not None
        assert e.path == "/insights"


class TestCurrentPageRecordField(BaseTestCase):
    async def test_schema(self) -> None:
        expected_fields = [
            "title",
            "pageview_id",
        ]

        assert_schemas_match(
            (CurrentPageRecordField.schema(),),
            (
                SchemaField(
                    name="current_page",
                    field_type=SqlTypeNames.RECORD,
                    mode=BigQueryFieldMode.NULLABLE,
                    fields=(
                        UrlRecordField.schema(name="url", description=self.anystr()),
                        *[
                            SchemaField(
                                name=k,
                                field_type=SqlTypeNames.STRING,
                                mode=BigQueryFieldMode.NULLABLE,
                            )
                            for k in expected_fields
                        ],
                    ),
                ),
            ),
        )

    async def test_field(self) -> None:
        url = f"https://{self.anyhex("url.domain")}.fyi:9090{self.anypath("url.path")}?{self.anyhex("url.qp")}={self.anyhex("url.qpv")}#{self.anyhex("url.hash")}"

        e = CurrentPageRecordField.from_api_resource(
            resource=CurrentPageProperties(
                url=url,
                title=self.anystr("current_page.title"),
                pageview_id=self.anystr("current_page.pageview_id"),
            ),
        )
        assert e is not None
        assert e.url == UrlRecordField.from_api_resource(url)
        assert e.title == self.getstr("current_page.title")
        assert e.pageview_id == self.getstr("current_page.pageview_id")

        assert dataclasses.asdict(e) == {
            "url": {
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
            },
            "title": self.getstr("current_page.title"),
            "pageview_id": self.getstr("current_page.pageview_id"),
        }

    async def test_field_no_values(self) -> None:
        e = CurrentPageRecordField.from_api_resource(
            resource=CurrentPageProperties(
                url=None,
                title=None,
                pageview_id=None,
            ),
        )
        assert e is not None
        assert e.url is None
        assert e.title is None
        assert e.pageview_id is None


class TestBigQueryRecordMetadataRecordField(BaseTestCase):
    async def test_schema(self) -> None:
        assert_schemas_match(
            (MetadataRecordField.schema(),),
            (
                SchemaField(
                    name="metadata",
                    field_type=SqlTypeNames.RECORD,
                    mode=BigQueryFieldMode.NULLABLE,
                    fields=(
                        SchemaField(
                            name="source_app_name",
                            field_type=SqlTypeNames.STRING,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        SchemaField(
                            name="source_app_version",
                            field_type=SqlTypeNames.STRING,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        SchemaField(
                            name="source_app_release_timestamp",
                            field_type=SqlTypeNames.TIMESTAMP,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                    ),
                ),
            ),
        )

    async def test_field(self) -> None:
        e = MetadataRecordField(
            source_app_name=self.anyhex("source_app_name"),
            source_app_version=self.anyhex("source_app_version"),
            source_app_release_timestamp=self.anytime("source_app_release_timestamp"),
        )

        assert dataclasses.asdict(e) == {
            "source_app_name": self.gethex("source_app_name"),
            "source_app_version": self.gethex("source_app_version"),
            "source_app_release_timestamp": self.gettime("source_app_release_timestamp"),
        }


class TestOpenAIRequestPropertiesRecordField(BaseTestCase):
    async def test_schema(self) -> None:
        assert_schemas_match(
            (OpenAIRequestPropertiesRecordField.schema(),),
            (
                SchemaField(
                    name="openai_request",
                    field_type=SqlTypeNames.RECORD,
                    mode=BigQueryFieldMode.NULLABLE,
                    fields=(
                        SchemaField(
                            name="start_timestamp",
                            field_type=SqlTypeNames.TIMESTAMP,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        SchemaField(
                            name="end_timestamp",
                            field_type=SqlTypeNames.TIMESTAMP,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        SchemaField(
                            name="duration_ms",
                            field_type=SqlTypeNames.FLOAT,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        SchemaField(
                            name="status_code",
                            field_type=SqlTypeNames.INTEGER,
                            mode=BigQueryFieldMode.NULLABLE,
                        ),
                        MultiScalarTypeKeyValueRecordField.schema(
                            name="request_params",
                            description=self.anystr(),
                        ),
                    ),
                ),
            ),
        )

    async def test_field(self) -> None:
        e = OpenAIRequestPropertiesRecordField(
            start_timestamp=self.anytime("start_timestamp"),
            end_timestamp=self.anytime("end_timestamp"),
            duration_ms=self.anyint("duration_ms"),
            status_code=200,
            request_params=MultiScalarTypeKeyValueRecordField.list_from_scalar_dict(
                {
                    self.anyhex("k1"): self.anystr("v1"),
                    self.anyhex("k2"): self.anyfloat("v2"),
                }
            ),
        )

        assert dataclasses.asdict(e) == {
            "start_timestamp": self.gettime("start_timestamp"),
            "end_timestamp": self.gettime("end_timestamp"),
            "duration_ms": self.getint("duration_ms"),
            "status_code": 200,
            "request_params": [
                {
                    "key": self.gethex("k1"),
                    "value": {
                        "string_value": self.getstr("v1"),
                        "bool_value": None,
                        "numeric_value": None,
                    },
                },
                {
                    "key": self.gethex("k2"),
                    "value": {
                        "string_value": None,
                        "bool_value": None,
                        "numeric_value": Numeric(self.getfloat("v2")),
                    },
                },
            ],
        }


class TestNumericType(BaseTestCase):
    def test_constructor(self) -> None:
        d = Decimal("90")
        n = Numeric(d)
        assert n == "90"

        # Test a few string methods to make sure inheritance works.
        assert n.startswith("9")
        assert n.endswith("0")

        @dataclasses.dataclass
        class Person:
            age: Numeric

        p = Person(age=n)
        assert dataclasses.asdict(p) == {
            "age": "90",
        }
