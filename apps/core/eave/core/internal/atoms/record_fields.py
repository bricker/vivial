from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.core.internal.atoms.api_types import (
    CurrentPageProperties,
    DeviceBrandProperties,
    DeviceProperties,
    SessionProperties,
    TargetProperties,
    TrafficSourceProperties,
    UrlProperties,
)
from eave.core.internal.atoms.table_handle import BigQueryFieldMode
from eave.stdlib.typing import JsonScalar


@dataclass(kw_only=True)
class RecordField(ABC):
    @staticmethod
    @abstractmethod
    def schema(*args: Any, **kwargs: Any) -> SchemaField:
        ...


@dataclass(kw_only=True)
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
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="bool_value",
                    field_type=SqlTypeNames.BOOLEAN,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="int_value",
                    field_type=SqlTypeNames.INTEGER,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SchemaField(
                    name="float_value",
                    field_type=SqlTypeNames.FLOAT,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
            ),
        )

    string_value: str | None = None
    int_value: int | None = None
    float_value: float | None = None
    bool_value: bool | None = None


@dataclass(kw_only=True)
class MultiTypeKeyValueRecordField(RecordField):
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
                    mode=BigQueryFieldMode.REQUIRED,
                ),
                TypedValueRecordField.schema(),
            ),
        )

    @classmethod
    def list_from_scalar_dict(cls, d: dict[str, JsonScalar] | None) -> list["MultiTypeKeyValueRecordField"]:
        if not d:
            return []

        containers: list[MultiTypeKeyValueRecordField] = []

        for [key, value] in d.items():
            typed_value = TypedValueRecordField()

            if isinstance(value, str):
                typed_value.string_value = value
            elif isinstance(value, int):
                typed_value.int_value = value
            elif isinstance(value, float):
                typed_value.float_value = value
            elif isinstance(value, bool):
                typed_value.bool_value = value
            elif value is None:
                # All fields are initialized with None, nothing to do here.
                pass
            else:
                # This is for safety, in case another type is added to the JsonScalar union
                typed_value.string_value = str(value)

            container = MultiTypeKeyValueRecordField(key=key, value=typed_value)
            containers.append(container)

        return containers

    key: str
    value: TypedValueRecordField | None


@dataclass(kw_only=True)
class SingleTypeKeyValueRecordField[T: str | bool | int | float](RecordField):
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
                    mode=BigQueryFieldMode.REQUIRED,
                ),
                SchemaField(
                    name="value",
                    field_type=value_type,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
            ),
        )

    @classmethod
    def list_from_scalar_dict(cls, d: dict[str, T | None] | None) -> list["SingleTypeKeyValueRecordField[T]"]:
        if not d:
            return []

        containers: list[SingleTypeKeyValueRecordField[T]] = []

        for [key, value] in d.items():
            container = SingleTypeKeyValueRecordField(key=key, value=value)
            containers.append(container)

        return containers

    key: str
    value: T | None


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
    def from_api_resource(
        cls, resource: SessionProperties | None, event_timestamp: float | None
    ) -> "SessionRecordField | None":
        if not resource:
            return None

        if event_timestamp is not None and resource.start_timestamp is not None:
            duration_ms = (event_timestamp - resource.start_timestamp) * 1000
        else:
            duration_ms = None

        return SessionRecordField(
            id=resource.id,
            start_timestamp=resource.start_timestamp,
            duration_ms=duration_ms,
        )


@dataclass(kw_only=True)
class UserRecordField(RecordField):
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
                SingleTypeKeyValueRecordField.schema(
                    name="other_utm_params",
                    description="Catch-all for additional utm_* query params.",
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
    # keyword: str | None
    # matchtype: str | None
    # campaign: str | None
    # campaign_id: str | None
    # pid: str | None
    # cid: str | None
    utm_campaign: str | None
    utm_source: str | None
    utm_medium: str | None
    utm_term: str | None
    utm_content: str | None
    other_utm_params: list[SingleTypeKeyValueRecordField[str]] | None

    @classmethod
    def from_api_resource(cls, resource: TrafficSourceProperties | None) -> "TrafficSourceRecordField | None":
        if not resource:
            return None

        tp = resource.tracking_params.copy() if resource.tracking_params else None

        return cls(
            timestamp=resource.timestamp,
            browser_referrer=resource.browser_referrer,
            gclid=tp.pop("gclid", None) if tp else None,
            fbclid=tp.pop("fbclid", None) if tp else None,
            msclkid=tp.pop("msclkid", None) if tp else None,
            dclid=tp.pop("dclid", None) if tp else None,
            ko_click_id=tp.pop("ko_click_id", None) if tp else None,
            rtd_cid=tp.pop("rtd_cid", None) if tp else None,
            li_fat_id=tp.pop("li_fat_id", None) if tp else None,
            ttclid=tp.pop("ttclid", None) if tp else None,
            twclid=tp.pop("twclid", None) if tp else None,
            wbraid=tp.pop("wbraid", None) if tp else None,
            gbraid=tp.pop("gbraid", None) if tp else None,
            utm_campaign=tp.pop("utm_campaign", None) if tp else None,
            utm_source=tp.pop("utm_source", None) if tp else None,
            utm_medium=tp.pop("utm_medium", None) if tp else None,
            utm_term=tp.pop("utm_term", None) if tp else None,
            utm_content=tp.pop("utm_content", None) if tp else None,
            other_utm_params=SingleTypeKeyValueRecordField[str].list_from_scalar_dict(tp) if tp else None,
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
    def from_api_resource(cls, resource: DeviceBrandProperties) -> "BrandsRecordField":
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
    def from_api_resource(cls, resource: DeviceProperties | None) -> "DeviceRecordField | None":
        if not resource:
            return None

        return cls(
            user_agent=resource.user_agent,
            brands=[BrandsRecordField.from_api_resource(b) for b in resource.brands] if resource.brands else None,
            form_factor=resource.form_factor,
            mobile=resource.mobile,
            model=resource.model,
            platform=resource.platform,
            platform_version=resource.platform_version,
            screen_width=resource.screen_width,
            screen_height=resource.screen_height,
            screen_avail_width=resource.screen_avail_width,
            screen_avail_height=resource.screen_avail_height,
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
                SingleTypeKeyValueRecordField.schema(
                    name="attributes",
                    description="All attributes explicitly defined on this target in the DOM.",
                    value_type=SqlTypeNames.STRING,
                ),
            ),
        )

    type: str | None
    id: str | None
    content: str | None
    attributes: list[SingleTypeKeyValueRecordField[str]] | None

    @classmethod
    def from_api_resource(cls, resource: TargetProperties | None) -> "TargetRecordField | None":
        if not resource:
            return None

        return cls(
            type=resource.type,
            id=resource.id,
            content=resource.content,
            attributes=SingleTypeKeyValueRecordField[str].list_from_scalar_dict(resource.attributes)
            if resource.attributes
            else None,
        )


@dataclass(kw_only=True)
class UrlRecordField(RecordField):
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
                    description="The raw URL. Includes all parts except username or password. This is primarily for reference; the other fields in this record are more useful for queries. eg: https://dashboard.eave.fyi:9090/insights#footer?query=users",
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
                    description="The URL domain (aka hostname). Does not include the protocol, path, or port. eg: eave.fyi, dashboard.eave.fyi",
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
                    description="The URL hash (aka anchor). Includes the leading hash symbol. eg: #header1, #lowkeyme",
                    field_type=SqlTypeNames.STRING,
                    mode=BigQueryFieldMode.NULLABLE,
                ),
                SingleTypeKeyValueRecordField.schema(
                    name="query_params",
                    description="A list of the URL query parameter names and values.",
                    value_type=SqlTypeNames.STRING,
                ),
            ),
        )

    raw: str | None
    protocol: str | None
    domain: str | None
    path: str | None
    hash: str | None
    query_params: list[SingleTypeKeyValueRecordField[str]] | None

    @classmethod
    def from_api_resource(cls, resource: UrlProperties | None) -> "UrlRecordField | None":
        if not resource:
            return None

        return cls(
            raw=resource.raw,
            protocol=resource.protocol,
            domain=resource.domain,
            path=resource.path,
            hash=resource.hash,
            query_params=SingleTypeKeyValueRecordField[str].list_from_scalar_dict(resource.query_params)
            if resource.query_params
            else None,
        )


@dataclass(kw_only=True)
class CurrentPageRecordField(RecordField):
    @staticmethod
    def schema() -> SchemaField:
        return SchemaField(
            name="page",
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

    url: UrlRecordField | None
    title: str | None
    pageview_id: str | None

    @classmethod
    def from_api_resource(cls, resource: CurrentPageProperties | None) -> "CurrentPageRecordField | None":
        if not resource:
            return None

        return cls(
            url=UrlRecordField.from_api_resource(resource.url) if resource.url else None,
            title=resource.title,
            pageview_id=resource.pageview_id,
        )
