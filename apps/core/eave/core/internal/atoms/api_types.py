# These classes are representations of the API payload from the Browser collector.
# We don't use dataclasses because we want to ignore any unexpected attributes, which dataclasses don't natively allow.

from enum import StrEnum
from typing import Any, Self

from eave.stdlib.typing import JsonScalar


class BrowserAction(StrEnum):
    CLICK = "CLICK"
    FORM_SUBMIT = "FORM_SUBMIT"
    NAVIGATION = "NAVIGATION"

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

        if (v := data.get("brands")) and isinstance(v, list):
            self.brands = [DeviceBrandProperties(d) for d in v]


class UrlProperties:
    raw: str | None = None
    protocol: str | None = None
    domain: str | None = None
    path: str | None = None
    hash: str | None = None
    query_params: dict[str, str | None] | None = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.raw = data.get("raw")
        self.protocol = data.get("protocol")
        self.domain = data.get("domain")
        self.path = data.get("path")
        self.hash = data.get("hash")
        self.query_params = data.get("query_params")


class CurrentPageProperties:
    url: UrlProperties | None = None
    title: str | None = None
    pageview_id: str | None = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.title = data.get("title")
        self.pageview_id = data.get("pageview_id")

        if (v := data.get("url")) and isinstance(v, dict):
            self.url = UrlProperties(v)


class SessionProperties:
    id: str | None = None
    start_timestamp: float | None = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.id = data.get("id")
        self.start_timestamp = data.get("start_timestamp")


class UserProperties:
    account_id: str | None = None
    visitor_id: str | None = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.account_id = data.get("account_id")
        self.visitor_id = data.get("visitor_id")


class TrafficSourceProperties:
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
    utm_campaign: str | None = None
    utm_source: str | None = None
    utm_medium: str | None = None
    utm_term: str | None = None
    utm_content: str | None = None
    other_utm_params: dict[str, str | None] | None = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.timestamp = data.get("timestamp")
        self.browser_referrer = data.get("browser_referrer")
        self.gclid = data.get("gclid")
        self.fbclid = data.get("fbclid")
        self.msclkid = data.get("msclkid")
        self.dclid = data.get("dclid")
        self.ko_click_id = data.get("ko_click_id")
        self.rtd_cid = data.get("rtd_cid")
        self.li_fat_id = data.get("li_fat_id")
        self.ttclid = data.get("ttclid")
        self.twclid = data.get("twclid")
        self.wbraid = data.get("wbraid")
        self.gbraid = data.get("gbraid")
        self.utm_campaign = data.get("utm_campaign")
        self.utm_source = data.get("utm_source")
        self.utm_medium = data.get("utm_medium")
        self.utm_term = data.get("utm_term")
        self.utm_content = data.get("utm_content")
        self.other_utm_params = data.get("other_utm_params")


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


class BrowserEventPayload:
    action: BrowserAction | None = None
    timestamp: float | None = None
    target: TargetProperties | None = None
    device: DeviceProperties | None = None
    current_page: CurrentPageProperties | None = None
    session: SessionProperties | None = None
    user: UserProperties | None = None
    traffic_source: TrafficSourceProperties | None = None
    extra: dict[str, JsonScalar | None] | None = None

    def __init__(self, data: dict[str, Any]) -> None:
        self.timestamp = data.get("timestamp")
        self.extra = data.get("extra")

        if v := data.get("action"):
            self.action = BrowserAction.from_str(v)

        if (v := data.get("target")) and isinstance(v, dict):
            self.target = TargetProperties(v)

        if (v := data.get("device")) and isinstance(v, dict):
            self.device = DeviceProperties(v)

        if (v := data.get("current_page")) and isinstance(v, dict):
            self.current_page = CurrentPageProperties(v)

        if (v := data.get("session")) and isinstance(v, dict):
            self.session = SessionProperties(v)

        if (v := data.get("user")) and isinstance(v, dict):
            self.user = UserProperties(v)

        if (v := data.get("traffic_source")) and isinstance(v, dict):
            self.traffic_source = TrafficSourceProperties(v)
