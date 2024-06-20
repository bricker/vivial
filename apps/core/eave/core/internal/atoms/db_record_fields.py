"""
Class representations of BigQuery data. These convert the API payloads into datastructures ready to insert into BigQuery.
Many of these classes are not dataclasses, because they accept a payload class, not individual properties, and convert it into a BigQuery Record field.
The fields that _are_ dataclasses are so because they don't have a respective API payload class, and are therefore initialized with individual properties.

Additionally, the BigQuery record field schemas are defined on these classes.
These schemas are authoritative: changing these will change the respective schema in BigQuery.
"""

from dataclasses import dataclass
from urllib.parse import parse_qsl, urlparse

from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.core.internal.atoms.api_types import (
    CurrentPageProperties,
    DeviceBrandProperties,
    DeviceProperties,
    SessionProperties,
    TargetProperties,
    TrafficSourceProperties,
)
from eave.core.internal.atoms.shared import BigQueryFieldMode
from eave.stdlib.typing import JsonScalar


@dataclass(init=False)
class TypedValueRecordField:
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
            ),
        )

    string_value: str | None = None
    bool_value: bool | None = None
    numeric_value: int | float | None = None

    def __init__(self, value: str | int | float | bool | None) -> None:
        if isinstance(value, str):
            self.string_value = value
        elif isinstance(value, bool):
            # Reminder: bool is a subclass of int! bool check must come before the int check.
            self.bool_value = value
        elif isinstance(value, (float, int)):
            # Reminder: bool is a subclass of int! bool check must come before the int check.
            self.numeric_value = value
        else:
            # Handles None, as well as any future unhandled types.
            # All fields are initialized with None, nothing to do here.
            pass


@dataclass(kw_only=True)
class MultiScalarTypeKeyValueRecordField:
    """
    This is a dataclass because it doesn't come from an API payload
    """

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

    key: str
    value: TypedValueRecordField | None

    @classmethod
    def list_from_scalar_dict(cls, d: dict[str, JsonScalar]) -> list["MultiScalarTypeKeyValueRecordField"]:
        containers: list[MultiScalarTypeKeyValueRecordField] = []

        for [key, value] in d.items():
            typed_value = TypedValueRecordField(value)
            container = MultiScalarTypeKeyValueRecordField(key=key, value=typed_value)
            containers.append(container)

        return containers


@dataclass(kw_only=True)
class SingleScalarTypeKeyValueRecordField[T: str | bool | int | float]:
    """
    This is a dataclass because it doesn't come from an API payload
    """

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

    key: str
    value: T | None

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


@dataclass(init=False)
class SessionRecordField:
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

    id: str | None = None
    start_timestamp: float | None = None
    duration_ms: float | None = None

    def __init__(self, resource: SessionProperties, event_timestamp: float | None) -> None:
        self.id = resource.id
        self.start_timestamp = resource.start_timestamp

        if event_timestamp and resource.start_timestamp:
            self.duration_ms = (event_timestamp - resource.start_timestamp) * 1000


@dataclass(kw_only=True)
class UserRecordField:
    """
    This is a dataclass because it doesn't come from an API payload
    """

    @classmethod
    def schema(cls) -> SchemaField:
        return SchemaField(
            name="user",
            description="User properties.",
            field_type=SqlTypeNames.RECORD,
            mode=BigQueryFieldMode.NULLABLE,
            fields=(
                SchemaField(
                    name="account_id",
                    description="The user's account ID, as provided by the customer's database. Generally this is only available when the user is logged in.",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="visitor_id",
                    description="A unique ID per device assigned by Eave. This ID is persisted across sessions on the same device.",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
            ),
        )

    account_id: str | None
    visitor_id: str | None


@dataclass(init=False)
class TrafficSourceRecordField:
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
                # SchemaField(
                #     name="keyword",
                #     description="Non-standard query parameter",
                #     field_type=SqlTypeNames.STRING,
                #     mode=BigQueryFieldMode.NULLABLE,
                # ),
                # SchemaField(
                #     name="matchtype",
                #     description="Non-standard query parameter",
                #     field_type=SqlTypeNames.STRING,
                #     mode=BigQueryFieldMode.NULLABLE,
                # ),
                # SchemaField(
                #     name="campaign_id",
                #     description="Non-standard query parameter",
                #     field_type=SqlTypeNames.STRING,
                #     mode=BigQueryFieldMode.NULLABLE,
                # ),
                # SchemaField(
                #     name="pid",
                #     description="Non-standard query parameter",
                #     field_type=SqlTypeNames.STRING,
                #     mode=BigQueryFieldMode.NULLABLE,
                # ),
                # SchemaField(
                #     name="cid",
                #     description="Non-standard query parameter",
                #     field_type=SqlTypeNames.STRING,
                #     mode=BigQueryFieldMode.NULLABLE,
                # ),
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

    timestamp: float | None = None
    browser_referrer: str | None = None
    gclid: str | None = None
    fbclid: str | None = None
    msclkid: str | None = None
    dclid: str | None = None
    ko_click_id: str | None = None
    rtd_cid: str | None = None
    li_fat_id: str | None = None
    ttclid: str | None = None
    twclid: str | None = None
    wbraid: str | None = None
    gbraid: str | None = None
    # keyword: str | None = None
    # matchtype: str | None = None
    # campaign: str | None = None
    # campaign_id: str | None = None
    # pid: str | None = None
    # cid: str | None = None
    utm_campaign: str | None = None
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_term: str | None = None
    utm_content: str | None = None
    other_tracking_params: list[SingleScalarTypeKeyValueRecordField[str]] | None = None

    def __init__(self, resource: TrafficSourceProperties) -> None:
        self.timestamp = resource.timestamp
        self.browser_referrer = resource.browser_referrer

        if resource.tracking_params:
            tp = resource.tracking_params.copy()

            self.gclid = tp.pop("gclid", None)
            self.fbclid = tp.pop("fbclid", None)
            self.msclkid = tp.pop("msclkid", None)
            self.dclid = tp.pop("dclid", None)
            self.ko_click_id = tp.pop("ko_click_id", None)
            self.rtd_cid = tp.pop("rtd_cid", None)
            self.li_fat_id = tp.pop("li_fat_id", None)
            self.ttclid = tp.pop("ttclid", None)
            self.twclid = tp.pop("twclid", None)
            self.wbraid = tp.pop("wbraid", None)
            self.gbraid = tp.pop("gbraid", None)
            self.utm_campaign = tp.pop("utm_campaign", None)
            self.utm_source = tp.pop("utm_source", None)
            self.utm_medium = tp.pop("utm_medium", None)
            self.utm_term = tp.pop("utm_term", None)
            self.utm_content = tp.pop("utm_content", None)
            self.other_tracking_params = SingleScalarTypeKeyValueRecordField[str].list_from_scalar_dict(tp)


@dataclass(kw_only=True)
class GeoRecordField:
    """
    This is a dataclass because it doesn't come from an API payload.
    """

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


@dataclass(init=False)
class BrandsRecordField:
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

    brand: str | None = None
    version: str | None = None

    def __init__(self, resource: DeviceBrandProperties) -> None:
        self.brand = resource.brand
        self.version = resource.version


@dataclass(init=False)
class DeviceRecordField:
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

    user_agent: str | None = None
    brands: list[BrandsRecordField] | None = None
    platform: str | None = None
    platform_version: str | None = None
    mobile: bool | None = None
    form_factor: str | None = None
    model: str | None = None
    screen_width: int | None = None
    screen_height: int | None = None
    screen_avail_width: int | None = None
    screen_avail_height: int | None = None

    def __init__(self, resource: DeviceProperties) -> None:
        self.user_agent = resource.user_agent
        self.form_factor = resource.form_factor
        self.mobile = resource.mobile
        self.model = resource.model
        self.platform = resource.platform
        self.platform_version = resource.platform_version
        self.screen_width = resource.screen_width
        self.screen_height = resource.screen_height
        self.screen_avail_width = resource.screen_avail_width
        self.screen_avail_height = resource.screen_avail_height

        if resource.brands:
            self.brands = [BrandsRecordField(b) for b in resource.brands]


@dataclass(init=False)
class TargetRecordField:
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

    type: str | None = None
    id: str | None = None
    content: str | None = None
    attributes: list[SingleScalarTypeKeyValueRecordField[str]] | None = None

    def __init__(self, resource: TargetProperties) -> None:
        self.type = resource.type
        self.id = resource.id
        self.content = resource.content

        if resource.attributes:
            self.attributes = SingleScalarTypeKeyValueRecordField[str].list_from_scalar_dict(resource.attributes)


@dataclass(init=False)
class UrlRecordField:
    @staticmethod
    def schema() -> SchemaField:
        return SchemaField(
            name="url",
            description="The page URL when this event occurred.",
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

    raw: str | None = None
    protocol: str | None = None
    domain: str | None = None
    path: str | None = None
    hash: str | None = None
    query_params: list[SingleScalarTypeKeyValueRecordField[str]] | None = None

    def __init__(self, resource: str) -> None:
        parsed = urlparse(resource, allow_fragments=True)

        # Normalize the path
        path = parsed.path.removesuffix("/")

        self.raw = resource
        self.protocol = parsed.scheme
        self.domain = parsed.hostname
        self.path = path or None
        self.hash = parsed.fragment or None

        if parsed.query:
            qsl = parse_qsl(parsed.query, keep_blank_values=True)
            self.query_params = SingleScalarTypeKeyValueRecordField[str].list_from_kv_tuples(qsl)


@dataclass(init=False)
class CurrentPageRecordField:
    @staticmethod
    def schema() -> SchemaField:
        return SchemaField(
            name="current_page",
            description="Properties about the current page at the time this event occurred.",
            field_type=SqlTypeNames.RECORD,
            mode=BigQueryFieldMode.NULLABLE,
            fields=(
                UrlRecordField.schema(),
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

    url: UrlRecordField | None = None
    title: str | None = None
    pageview_id: str | None = None

    def __init__(self, resource: CurrentPageProperties) -> None:
        if resource.url:
            self.url = UrlRecordField(resource.url)

        self.title = resource.title
        self.pageview_id = resource.pageview_id
