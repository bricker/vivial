"""
Class representations of BigQuery data. These convert the API payloads into datastructures ready to insert into BigQuery.
Many of these classes are not dataclasses, because they accept a payload class, not individual properties, and convert it into a BigQuery Record field.
The fields that _are_ dataclasses are so because they don't have a respective API payload class, and are therefore initialized with individual properties.

Additionally, the BigQuery record field schemas are defined on these classes.
These schemas are authoritative: changing these will change the respective schema in BigQuery.
"""

import json
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Self
from urllib.parse import parse_qsl, urlparse

from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.core.internal.atoms.models.api_payload_types import (
    AccountProperties,
    CurrentPageProperties,
    DeviceBrandProperties,
    DeviceProperties,
    OpenAIRequestProperties,
    SessionProperties,
    StackFrameProperties,
    TargetProperties,
    TrafficSourceProperties,
)
from eave.stdlib.core_api.models.virtual_event import BigQueryFieldMode
from eave.stdlib.deidentification import REDACTABLE
from eave.stdlib.logging import LOGGER
from eave.stdlib.typing import JsonValue


class Numeric(str):
    """
    Decimal can't be used directly for atoms, because atoms and all of their attributes have to be completely compatible with dataclasses.
    Numeric is effectively an alias for `str`, or a wrapper around `Decimal` depending on how you look at it,
    and requires that a Decimal, int, or flat is passed-in to the constructor to indicate the intention to the caller (developer).
    It's passed-in to BigQuery as a plain string, which is an acceptable input format for NUMERIC data tyes.
    """

    __slots__ = ()  # Save memory

    def __new__(cls, value: Decimal | int | float) -> Self:
        return super().__new__(cls, str(value))


class RecordField:
    pass


@dataclass(init=False)
class TypedValueRecordField(RecordField):
    @staticmethod
    def schema() -> SchemaField:
        return SchemaField(
            name="value",
            field_type=SqlTypeNames.RECORD,
            mode=BigQueryFieldMode.NULLABLE,
            fields=(
                SchemaField(
                    name="string_value",
                    description="The value for the key, if the value is a string. Otherwise, null.",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="numeric_value",
                    description="The value for the key, if the value is a number type (eg int or float). Otherwise, null.",
                    field_type=SqlTypeNames.NUMERIC,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="bool_value",
                    description="The value for the key, if the value is a boolean. Otherwise, null.",
                    field_type=SqlTypeNames.BOOLEAN,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="json_value",
                    description="The value for the key, if the value is a JSON-serializable list or map. Otherwise, null.",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
            ),
        )

    string_value: str | None = field(metadata={REDACTABLE: True}, default=None)
    bool_value: bool | None = None
    numeric_value: Numeric | None = field(metadata={REDACTABLE: True}, default=None)
    json_value: str | None = field(metadata={REDACTABLE: True}, default=None)

    def __init__(self, value: JsonValue | None) -> None:
        # It is important to remember that these checks have to be exclusive - if multiple checks are done, it's possible
        # for multiple fields to have a value set. This is especially likely when working with bools and numbers.
        if isinstance(value, str):
            self.string_value = value
        elif isinstance(value, bool):
            # Reminder: bool is a subclass of int! bool check must come before the int check.
            self.bool_value = value
        elif isinstance(value, (float, int)):
            # Reminder: bool is a subclass of int! bool check must come before the int check.
            # The value is converted to string for the Decimal initializer because if given a float, Decimal forces the configured precision, which may be too
            self.numeric_value = Numeric(value)
        elif value is None:
            # Everything is None by default, so nothing is needed here.
            pass
        else:
            try:
                self.json_value = json.dumps(value)
            except TypeError as e:
                LOGGER.exception(e)


@dataclass(kw_only=True)
class MultiScalarTypeKeyValueRecordField(RecordField):
    @staticmethod
    def schema(*, name: str, description: str) -> SchemaField:
        return SchemaField(
            name=name,
            description=description,
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
        )

    key: str = field(metadata={REDACTABLE: True})
    value: TypedValueRecordField | None = field(metadata={REDACTABLE: True})

    @classmethod
    def list_from_dict(cls, d: dict[str, JsonValue]) -> list["MultiScalarTypeKeyValueRecordField"]:
        containers: list[MultiScalarTypeKeyValueRecordField] = []

        for [key, value] in d.items():
            typed_value = TypedValueRecordField(value)
            container = MultiScalarTypeKeyValueRecordField(key=key, value=typed_value)
            containers.append(container)

        return containers


@dataclass(kw_only=True)
class SingleScalarTypeKeyValueRecordField[T: str | bool | int | float]:
    @staticmethod
    def schema(*, name: str, description: str, value_type: SqlTypeNames) -> SchemaField:
        return SchemaField(
            name=name,
            description=description,
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
                    field_type=value_type,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
            ),
        )

    key: str = field(metadata={REDACTABLE: True})
    value: T | None = field(metadata={REDACTABLE: True})

    @classmethod
    def list_from_scalar_dict(cls, d: dict[str, T | None]) -> list["SingleScalarTypeKeyValueRecordField[T]"]:
        containers: list[SingleScalarTypeKeyValueRecordField[T]] = []

        for key, value in d.items():
            container = SingleScalarTypeKeyValueRecordField(key=key, value=value)
            containers.append(container)

        return containers

    @classmethod
    def list_from_kv_tuples(cls, d: list[tuple[str, T]]) -> list["SingleScalarTypeKeyValueRecordField[T]"]:
        containers: list[SingleScalarTypeKeyValueRecordField[T]] = []

        for key, value in d:
            container = SingleScalarTypeKeyValueRecordField(key=key, value=value)
            containers.append(container)

        return containers


@dataclass(kw_only=True)
class SessionRecordField(RecordField):
    @classmethod
    def schema(cls) -> SchemaField:
        return SchemaField(
            name="session",
            description="Details about the user session during which this event occurred.",
            field_type=SqlTypeNames.RECORD,
            mode=BigQueryFieldMode.NULLABLE,
            fields=(
                SchemaField(
                    name="id",
                    description="A unique ID given to this session by Eave.",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="start_timestamp",
                    description="When this session started.",
                    field_type=SqlTypeNames.TIMESTAMP,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="duration_ms",
                    description="The duration in milliseconds of the session at the time the user triggered this event.",
                    field_type=SqlTypeNames.FLOAT,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
            ),
        )

    id: str | None
    start_timestamp: float | None
    duration_ms: float | None

    @classmethod
    def from_api_resource(cls, resource: SessionProperties, event_timestamp: float | None) -> Self:
        if event_timestamp and resource.start_timestamp:
            duration_ms = (event_timestamp - resource.start_timestamp) * 1000
        else:
            duration_ms = None

        return cls(
            id=resource.id,
            start_timestamp=resource.start_timestamp,
            duration_ms=duration_ms,
        )


@dataclass(kw_only=True)
class AccountRecordField(RecordField):
    @classmethod
    def schema(cls) -> SchemaField:
        return SchemaField(
            name="account",
            description="User account properties.",
            field_type=SqlTypeNames.RECORD,
            mode=BigQueryFieldMode.NULLABLE,
            fields=(
                SchemaField(
                    name="account_id",
                    description="The user's account ID, as provided by the customer's database. Generally this is only available when the user is logged in.",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                MultiScalarTypeKeyValueRecordField.schema(
                    name="extra",
                    description="Additional arbitrary account attributes.",
                ),
            ),
        )

    account_id: str | None
    extra: list[MultiScalarTypeKeyValueRecordField] | None = field(metadata={REDACTABLE: True})

    @classmethod
    def from_api_resource(cls, resource: AccountProperties) -> Self:
        return cls(
            account_id=resource.account_id,
            extra=(MultiScalarTypeKeyValueRecordField.list_from_dict(resource.extra) if resource.extra else None),
        )


@dataclass(kw_only=True)
class TrafficSourceRecordField(RecordField):
    @classmethod
    def schema(cls) -> SchemaField:
        return SchemaField(
            name="traffic_source",
            description="UTM Parameters and related discovery details.",
            field_type=SqlTypeNames.RECORD,
            mode=BigQueryFieldMode.NULLABLE,
            fields=(
                SchemaField(
                    name="timestamp",
                    description="When these tracking params were saved.",
                    field_type=SqlTypeNames.TIMESTAMP,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="browser_referrer",
                    description="The page referrer reported by the browser.",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="gclid",
                    description="Google Click ID (Query parameter gclid)",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="fbclid",
                    description="Facebook Click ID (Query parameter fbclid)",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="msclkid",
                    description="Microsoft Click ID (Query parameter msclkid)",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="dclid",
                    description="Google Campaign Manager dclid - https://support.google.com/campaignmanager/answer/9182069 (Query parameter dclid)",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="ko_click_id",
                    description="Kochava Click ID (Query parameter ko_click_id)",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="rtd_cid",
                    description="Reddit Click ID (Query parameter rtd_cid)",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="li_fat_id",
                    description="LinkedIn First-Party Ad Tracking ID (Query parameter li_fat_id)",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="ttclid",
                    description="TikTok Click ID (Query parameter ttclid)",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="twclid",
                    description="Twitter Click ID (Query parameter twclid)",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="wbraid",
                    description="Google wbraid - https://support.google.com/google-ads/answer/10417364 (Query parameter wbraid)",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="gbraid",
                    description="Google gbraid - https://support.google.com/google-ads/answer/10417364#gbraid (Query parameter gbraid)",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="utm_campaign",
                    description="Query parameter utm_campaign",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="utm_source",
                    description="Query parameter utm_source",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="utm_medium",
                    description="Query parameter utm_medium",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="utm_term",
                    description="Query parameter utm_term",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="utm_content",
                    description="Query parameter utm_content",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SingleScalarTypeKeyValueRecordField.schema(
                    name="other_tracking_params",
                    description="Catch-all for additional tracking query params.",
                    value_type=SqlTypeNames.STRING,
                ),
            ),
        )

    timestamp: float | None
    browser_referrer: str | None
    gclid: str | None
    fbclid: str | None
    msclkid: str | None
    dclid: str | None
    ko_click_id: str | None
    rtd_cid: str | None
    li_fat_id: str | None
    ttclid: str | None
    twclid: str | None
    wbraid: str | None
    gbraid: str | None
    utm_campaign: str | None
    utm_source: str | None
    utm_medium: str | None
    utm_term: str | None
    utm_content: str | None
    other_tracking_params: list[SingleScalarTypeKeyValueRecordField[str]] | None

    @classmethod
    def from_api_resource(cls, resource: TrafficSourceProperties) -> Self:
        tp = resource.tracking_params.copy() if resource.tracking_params else None

        gclid = tp.pop("gclid", None) if tp else None
        fbclid = tp.pop("fbclid", None) if tp else None
        msclkid = tp.pop("msclkid", None) if tp else None
        dclid = tp.pop("dclid", None) if tp else None
        ko_click_id = tp.pop("ko_click_id", None) if tp else None
        rtd_cid = tp.pop("rtd_cid", None) if tp else None
        li_fat_id = tp.pop("li_fat_id", None) if tp else None
        ttclid = tp.pop("ttclid", None) if tp else None
        twclid = tp.pop("twclid", None) if tp else None
        wbraid = tp.pop("wbraid", None) if tp else None
        gbraid = tp.pop("gbraid", None) if tp else None
        utm_campaign = tp.pop("utm_campaign", None) if tp else None
        utm_source = tp.pop("utm_source", None) if tp else None
        utm_medium = tp.pop("utm_medium", None) if tp else None
        utm_term = tp.pop("utm_term", None) if tp else None
        utm_content = tp.pop("utm_content", None) if tp else None
        other_tracking_params = SingleScalarTypeKeyValueRecordField[str].list_from_scalar_dict(tp) if tp else None

        return cls(
            timestamp=resource.timestamp,
            browser_referrer=resource.browser_referrer,
            gclid=gclid,
            fbclid=fbclid,
            msclkid=msclkid,
            dclid=dclid,
            ko_click_id=ko_click_id,
            rtd_cid=rtd_cid,
            li_fat_id=li_fat_id,
            ttclid=ttclid,
            twclid=twclid,
            wbraid=wbraid,
            gbraid=gbraid,
            utm_campaign=utm_campaign,
            utm_source=utm_source,
            utm_medium=utm_medium,
            utm_term=utm_term,
            utm_content=utm_content,
            other_tracking_params=other_tracking_params,
        )


@dataclass(kw_only=True)
class GeoRecordField(RecordField):
    @staticmethod
    def schema() -> SchemaField:
        return SchemaField(
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
        )

    region: str | None
    subdivision: str | None
    city: str | None
    coordinates: str | None


@dataclass(kw_only=True)
class BrandsRecordField(RecordField):
    @staticmethod
    def schema() -> SchemaField:
        return SchemaField(
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
        )

    brand: str | None
    version: str | None

    @classmethod
    def from_api_resource(cls, resource: DeviceBrandProperties) -> Self:
        return cls(
            brand=resource.brand,
            version=resource.version,
        )


@dataclass(kw_only=True)
class DeviceRecordField(RecordField):
    @staticmethod
    def schema() -> SchemaField:
        return SchemaField(
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
                BrandsRecordField.schema(),
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
        )

    user_agent: str | None
    brands: list[BrandsRecordField] | None
    platform: str | None
    platform_version: str | None
    mobile: bool | None
    form_factor: str | None
    model: str | None
    screen_width: int | None
    screen_height: int | None
    screen_avail_width: int | None
    screen_avail_height: int | None

    @classmethod
    def from_api_resource(cls, resource: DeviceProperties) -> Self:
        return cls(
            user_agent=resource.user_agent,
            form_factor=resource.form_factor,
            mobile=resource.mobile,
            model=resource.model,
            platform=resource.platform,
            platform_version=resource.platform_version,
            screen_width=resource.screen_width,
            screen_height=resource.screen_height,
            screen_avail_width=resource.screen_avail_width,
            screen_avail_height=resource.screen_avail_height,
            brands=([BrandsRecordField.from_api_resource(b) for b in resource.brands] if resource.brands else None),
        )


@dataclass(kw_only=True)
class TargetRecordField(RecordField):
    @staticmethod
    def schema() -> SchemaField:
        return SchemaField(
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
                    name="content",
                    description="The content of the target. This depends on the target type. For buttons, this is the button's text. For links, it is the link text. For images, it is the image 'src' attribute. For forms, it is the form 'action' attribute.",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SingleScalarTypeKeyValueRecordField.schema(
                    name="attributes",
                    description="All attributes explicitly defined on this target in the DOM.",
                    value_type=SqlTypeNames.STRING,
                ),
            ),
        )

    type: str | None
    id: str | None = field(metadata={REDACTABLE: True})
    content: str | None = field(metadata={REDACTABLE: True})
    attributes: list[SingleScalarTypeKeyValueRecordField[str]] | None = field(metadata={REDACTABLE: True})

    @classmethod
    def from_api_resource(cls, resource: TargetProperties) -> Self:
        return cls(
            type=resource.type,
            id=resource.id,
            content=resource.content,
            attributes=(
                SingleScalarTypeKeyValueRecordField[str].list_from_scalar_dict(resource.attributes)
                if resource.attributes
                else None
            ),
        )


@dataclass(kw_only=True)
class UrlRecordField(RecordField):
    @staticmethod
    def schema(name: str, description: str) -> SchemaField:
        return SchemaField(
            name=name,
            description=description,
            field_type=SqlTypeNames.RECORD,
            mode=BigQueryFieldMode.NULLABLE,
            fields=(
                SchemaField(
                    name="raw",
                    description="The full, unmodified URL. This is primarily for reference; the other fields in this record are more useful for queries. eg: https://dashboard.eave.fyi:9090/insights?query=users#footer",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="protocol",
                    description="The URL protocol (aka scheme). Does not include trailing colon or slashes. eg: https, http",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="domain",
                    description="The URL domain (aka hostname). Does not include the protocol, port, or path. eg: eave.fyi, dashboard.eave.fyi",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="path",
                    description="The URL path (aka pathname). Includes the leading slash. eg: /insights, /settings/account",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="hash",
                    description="The URL hash (aka fragment or anchor). Does NOT include the leading hash symbol. eg: header1, lowkeyme",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SingleScalarTypeKeyValueRecordField.schema(
                    name="query_params",
                    description="A list of the URL query parameter names and values. Names are NOT unique per record.",
                    value_type=SqlTypeNames.STRING,
                ),
            ),
        )

    raw: str | None = field(metadata={REDACTABLE: True})
    protocol: str | None
    domain: str | None = field(metadata={REDACTABLE: True})
    path: str | None = field(metadata={REDACTABLE: True})
    hash: str | None = field(metadata={REDACTABLE: True})
    query_params: list[SingleScalarTypeKeyValueRecordField[str]] | None = field(metadata={REDACTABLE: True})

    @classmethod
    def from_api_resource(cls, resource: str) -> Self:
        parsed = urlparse(resource, allow_fragments=True)

        # Normalize the path
        path = parsed.path.removesuffix("/")

        if parsed.query:
            qsl = parse_qsl(parsed.query, keep_blank_values=True)
            query_params = SingleScalarTypeKeyValueRecordField[str].list_from_kv_tuples(qsl)
        else:
            query_params = None

        return cls(
            raw=resource,
            protocol=parsed.scheme,
            domain=parsed.hostname,
            path=path or None,
            hash=parsed.fragment or None,
            query_params=query_params,
        )


@dataclass(kw_only=True)
class CurrentPageRecordField(RecordField):
    @staticmethod
    def schema() -> SchemaField:
        return SchemaField(
            name="current_page",
            description="Properties about the current page at the time this event occurred.",
            field_type=SqlTypeNames.RECORD,
            mode=BigQueryFieldMode.NULLABLE,
            fields=(
                UrlRecordField.schema(name="url", description="The page URL when this event occurred."),
                SchemaField(
                    name="title",
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
            ),
        )

    url: UrlRecordField | None = field(metadata={REDACTABLE: True})
    title: str | None = field(metadata={REDACTABLE: True})
    pageview_id: str | None

    @classmethod
    def from_api_resource(cls, resource: CurrentPageProperties) -> Self:
        return cls(
            url=UrlRecordField.from_api_resource(resource.url) if resource.url else None,
            title=resource.title,
            pageview_id=resource.pageview_id,
        )


@dataclass(kw_only=True)
class MetadataRecordField:
    @staticmethod
    def schema() -> SchemaField:
        return SchemaField(
            name="metadata",
            description="Internal metadata about this BigQuery record. Not reliable for event analysis.",
            field_type=SqlTypeNames.RECORD,
            mode=BigQueryFieldMode.NULLABLE,
            fields=(
                SchemaField(
                    name="source_app_name",
                    description="The name of the app that inserted this record.",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="source_app_version",
                    description="The version of the app that inserted this record.",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="source_app_release_timestamp",
                    description="The release timestamp of the app that inserted this record.",
                    field_type=SqlTypeNames.TIMESTAMP,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
            ),
        )

    source_app_name: str | None
    source_app_version: str | None
    source_app_release_timestamp: float | None


@dataclass(kw_only=True)
class StackFramesRecordField:
    @staticmethod
    def schema() -> SchemaField:
        return SchemaField(
            name="stack_frames",
            field_type=SqlTypeNames.RECORD,
            mode=BigQueryFieldMode.REPEATED,
            fields=(
                SchemaField(
                    name="filename",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                    description="The name of the file in which this stack frame was created.",
                ),
                SchemaField(
                    name="function",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                    description="The name of the function in which this stack frame was created.",
                ),
            ),
        )

    filename: str | None
    function: str | None

    @classmethod
    def from_api_resource(cls, resource: StackFrameProperties) -> Self:
        return cls(
            filename=resource.filename,
            function=resource.function,
        )


@dataclass(kw_only=True)
class OpenAIRequestPropertiesRecordField:
    @staticmethod
    def schema() -> SchemaField:
        return SchemaField(
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
                MultiScalarTypeKeyValueRecordField.schema(
                    name="request_params",
                    description="Request params sent to the OpenAI API. Some params are omitted for privacy.",
                ),
            ),
        )

    start_timestamp: float | None
    end_timestamp: float | None
    duration_ms: float | None
    request_params: list[MultiScalarTypeKeyValueRecordField] | None

    @classmethod
    def from_api_resource(cls, resource: OpenAIRequestProperties) -> Self:
        if resource.start_timestamp and resource.end_timestamp:
            duration_ms = (resource.end_timestamp - resource.start_timestamp) * 1000
        else:
            duration_ms = None

        return cls(
            start_timestamp=resource.start_timestamp,
            end_timestamp=resource.end_timestamp,
            duration_ms=duration_ms,
            request_params=(
                MultiScalarTypeKeyValueRecordField.list_from_dict(resource.request_params)
                if resource.request_params
                else None
            ),
        )
