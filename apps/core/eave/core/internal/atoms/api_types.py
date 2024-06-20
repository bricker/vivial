"""
Class representations of the API payloads from the collectors.
We don't use automatic dataclass initializers because we want to ignore any unexpected attributes, which dataclasses don't natively allow.

Additionally, these are true representations; in other words, these class don't do any conversion to BigQuery-ready datastructures.
That happens in the RecordField classes.
"""

import json
from enum import StrEnum
from typing import Any, Self

from eave.collectors.core.correlation_context.base import EAVE_COLLECTOR_COOKIE_PREFIX
from eave.collectors.core.datastructures import DatabaseOperation, HttpRequestMethod
from eave.stdlib.logging import LOGGER
from eave.stdlib.typing import JsonScalar


class BrowserAction(StrEnum):
    CLICK = "CLICK"
    FORM_SUBMISSION = "FORM_SUBMISSION"
    PAGE_VIEW = "PAGE_VIEW"

    @classmethod
    def from_str(cls, s: str) -> Self | None:
        try:
            return cls.__call__(value=s.upper())
        except ValueError:
            return None


class DeviceBrandProperties:
    brand: str | None = None
    version: str | None = None

    def __init__(self, data: dict[str, str]) -> None:
        self.brand = data.get("brand")
        self.version = data.get("version")


class DeviceProperties:
    user_agent: str | None = None
    brands: list[DeviceBrandProperties] | None = None
    platform: str | None = None
    mobile: bool | None = None
    form_factor: str | None = None
    model: str | None = None
    platform_version: str | None = None
    screen_width: int | None = None
    screen_height: int | None = None
    screen_avail_width: int | None = None
    screen_avail_height: int | None = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.user_agent = data.get("user_agent")
        self.platform = data.get("platform")
        self.mobile = data.get("mobile")
        self.form_factor = data.get("form_factor")
        self.model = data.get("model")
        self.platform_version = data.get("platform_version")
        self.screen_width = data.get("screen_width")
        self.screen_height = data.get("screen_height")
        self.screen_avail_width = data.get("screen_avail_width")
        self.screen_avail_height = data.get("screen_avail_height")
        self.brands = (
            [DeviceBrandProperties(d) for d in v] if (v := data.get("brands")) and isinstance(v, list) else None
        )


class CurrentPageProperties:
    url: str | None = None
    title: str | None = None
    pageview_id: str | None = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.title = data.get("title")
        self.pageview_id = data.get("pageview_id")
        self.url = data.get("url")


class SessionProperties:
    id: str | None = None
    start_timestamp: float | None = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.id = data.get("id")
        self.start_timestamp = data.get("start_timestamp")


# class UserProperties:
#     account_id: str | None
#     visitor_id: str | None

#     __init__ self(cls, data: dict[str, str]) -> None:
#             account_id=data.get("account_id"),
#             visitor_id=data.get("visitor_id"),
#         )


class TrafficSourceProperties:
    timestamp: float | None = None
    browser_referrer: str | None = None
    tracking_params: dict[str, str | None] | None = None
    # gclid: str | None = None
    # fbclid: str | None = None
    # msclkid: str | None = None
    # dclid: str | None = None
    # ko_click_id: str | None = None
    # rtd_cid: str | None = None
    # li_fat_id: str | None = None
    # ttclid: str | None = None
    # twclid: str | None = None
    # wbraid: str | None = None
    # gbraid: str | None = None
    # utm_campaign: str | None = None
    # utm_source: str | None = None
    # utm_medium: str | None = None
    # utm_term: str | None = None
    # utm_content: str | None = None
    # other_utm_params: dict[str, str | None] | None = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.timestamp = data.get("timestamp")
        self.browser_referrer = data.get("browser_referrer")
        self.tracking_params = data.get("tracking_params")
        # self.gclid=data.get("gclid")
        # self.fbclid=data.get("fbclid")
        # self.msclkid=data.get("msclkid")
        # self.dclid=data.get("dclid")
        # self.ko_click_id=data.get("ko_click_id")
        # self.rtd_cid=data.get("rtd_cid")
        # self.li_fat_id=data.get("li_fat_id")
        # self.ttclid=data.get("ttclid")
        # self.twclid=data.get("twclid")
        # self.wbraid=data.get("wbraid")
        # self.gbraid=data.get("gbraid")
        # self.utm_campaign=data.get("utm_campaign")
        # self.utm_source=data.get("utm_source")
        # self.utm_medium=data.get("utm_medium")
        # self.utm_term=data.get("utm_term")
        # self.utm_content=data.get("utm_content")
        # self.other_utm_params=data.get("other_utm_params")


class TargetProperties:
    type: str | None = None
    id: str | None = None
    content: str | None = None
    attributes: dict[str, str | None] | None = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.type = data.get("type")
        self.id = data.get("id")
        self.content = data.get("content")
        self.attributes = data.get("attributes")


class CorrelationContext:
    session: SessionProperties | None = None
    traffic_source: TrafficSourceProperties | None = None
    account_id: str | None = None
    visitor_id: str | None = None

    def __init__(self, data: dict[str, str]) -> None:
        if (v := data.get(f"{EAVE_COLLECTOR_COOKIE_PREFIX}traffic_source")) and isinstance(v, str):
            try:
                us = json.loads(v)
                self.traffic_source = TrafficSourceProperties(us)
            except Exception as e:
                # Catch JSON parse error
                LOGGER.exception(e)

        if (v := data.get(f"{EAVE_COLLECTOR_COOKIE_PREFIX}session")) and isinstance(v, str):
            try:
                us = json.loads(v)
                self.session = SessionProperties(us)
            except Exception as e:
                # Catch JSON parse error
                LOGGER.exception(e)

        if (v := data.get(f"{EAVE_COLLECTOR_COOKIE_PREFIX}account_id")) and isinstance(v, str):
            self.account_id = v

        if (v := data.get(f"{EAVE_COLLECTOR_COOKIE_PREFIX}visitor_id")) and isinstance(v, str):
            self.visitor_id = v


class BrowserEventPayload:
    action: BrowserAction | None = None
    timestamp: float | None = None
    target: TargetProperties | None = None
    device: DeviceProperties | None = None
    current_page: CurrentPageProperties | None = None
    extra: dict[str, JsonScalar | None] | None = None
    corr_ctx: CorrelationContext | None = None
    # session: SessionProperties | None = None
    # user: UserProperties | None = None
    # traffic_source: TrafficSourceProperties | None = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.action = BrowserAction.from_str(v) if (v := data.get("action")) else None

        self.timestamp = data.get("timestamp")

        self.target = TargetProperties(v) if (v := data.get("target")) and isinstance(v, dict) else None

        self.device = DeviceProperties(v) if (v := data.get("device")) and isinstance(v, dict) else None

        self.current_page = (
            CurrentPageProperties(v) if (v := data.get("current_page")) and isinstance(v, dict) else None
        )

        self.extra = data.get("extra")

        self.corr_ctx = CorrelationContext(v) if (v := data.get("corr_ctx")) and isinstance(v, dict) else None

        # if (v := data.get("session")) and isinstance(v, dict):
        #     self.session = SessionProperties(v)

        # if (v := data.get("user")) and isinstance(v, dict):
        #     self.user = UserProperties(v)

        # if (v := data.get("traffic_source")) and isinstance(v, dict):
        #     self.traffic_source = TrafficSourceProperties(v)


class DatabaseEventPayload:
    timestamp: float | None = None
    corr_ctx: CorrelationContext | None = None
    operation: DatabaseOperation | None = None
    db_name: str | None = None
    table_name: str | None = None
    statement: str | None = None
    statement_values: dict[str, Any] | None = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.timestamp = data.get("timestamp")
        self.operation = DatabaseOperation.from_str(v) if (v := data.get("operation")) else None
        self.db_name = data.get("db_name")
        self.table_name = data.get("table_name")
        self.statement = data.get("statement")
        self.statement_values = data.get("statement_values")

        if (v := data.get("corr_ctx")) and isinstance(v, dict):
            self.corr_ctx = CorrelationContext(v)


class HttpServerEventPayload:
    timestamp: float | None = None
    corr_ctx: CorrelationContext | None = None
    request_method: HttpRequestMethod | None = None
    request_url: str | None = None
    request_headers: dict[str, str | None] | None = None
    request_payload: str | None = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.timestamp = data.get("timestamp")
        self.request_method = HttpRequestMethod.from_str(v) if (v := data.get("request_method")) else None
        self.request_url = data.get("request_url")
        self.request_headers = data.get("request_headers")
        self.request_payload = data.get("request_payload")

        if (v := data.get("corr_ctx")) and isinstance(v, dict):
            self.corr_ctx = CorrelationContext(v)
