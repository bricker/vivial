# These classes are representations of the API payload from the Browser collector.
# We don't use dataclasses because we want to ignore any unexpected attributes, which dataclasses don't natively allow.

import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Self

from eave.collectors.core.correlation_context.base import EAVE_COLLECTOR_COOKIE_PREFIX
from eave.stdlib.logging import LOGGER
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


@dataclass(kw_only=True)
class DeviceBrandProperties:
    brand: str | None
    version: str | None

    @classmethod
    def from_api_payload(cls, data: dict[str, str]) -> Self:
        return cls(
            brand=data.get("brand"),
            version=data.get("version"),
        )


@dataclass(kw_only=True)
class DeviceProperties:
    user_agent: str | None
    brands: list[DeviceBrandProperties] | None
    platform: str | None
    mobile: bool | None
    form_factor: str | None
    model: str | None
    platform_version: str | None
    screen_width: int | None
    screen_height: int | None
    screen_avail_width: int | None
    screen_avail_height: int | None

    @classmethod
    def from_api_payload(cls, data: dict[str, Any]) -> Self:
        return cls(
            user_agent=data.get("user_agent"),
            platform=data.get("platform"),
            mobile=data.get("mobile"),
            form_factor=data.get("form_factor"),
            model=data.get("model"),
            platform_version=data.get("platform_version"),
            screen_width=data.get("screen_width"),
            screen_height=data.get("screen_height"),
            screen_avail_width=data.get("screen_avail_width"),
            screen_avail_height=data.get("screen_avail_height"),
            brands=[DeviceBrandProperties.from_api_payload(d) for d in v]
            if (v := data.get("brands")) and isinstance(v, list)
            else None,
        )


@dataclass(kw_only=True)
class CurrentPageProperties:
    url: str | None
    title: str | None
    pageview_id: str | None

    @classmethod
    def from_api_payload(cls, data: dict[str, Any]) -> Self:
        return cls(
            title=data.get("title"),
            pageview_id=data.get("pageview_id"),
            url=data.get("url"),
        )


@dataclass(kw_only=True)
class SessionProperties:
    id: str | None
    start_timestamp: float | None

    @classmethod
    def from_api_payload(cls, data: dict[str, Any]) -> Self:
        return cls(
            id=data.get("id"),
            start_timestamp=data.get("start_timestamp"),
        )


# @dataclass(kw_only=True)
# class UserProperties:
#     account_id: str | None
#     visitor_id: str | None

#     @classmethod
#     def from_api_payload(cls, data: dict[str, str]) -> Self:
#         return cls(
#             account_id=data.get("account_id"),
#             visitor_id=data.get("visitor_id"),
#         )


@dataclass(kw_only=True)
class TrafficSourceProperties:
    timestamp: float | None
    browser_referrer: str | None
    tracking_params: dict[str, str | None] | None
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

    @classmethod
    def from_api_payload(cls, data: dict[str, Any]) -> Self:
        return cls(
            timestamp=data.get("timestamp"),
            browser_referrer=data.get("browser_referrer"),
            tracking_params=data.get("tracking_params"),
            # gclid=data.get("gclid"),
            # fbclid=data.get("fbclid"),
            # msclkid=data.get("msclkid"),
            # dclid=data.get("dclid"),
            # ko_click_id=data.get("ko_click_id"),
            # rtd_cid=data.get("rtd_cid"),
            # li_fat_id=data.get("li_fat_id"),
            # ttclid=data.get("ttclid"),
            # twclid=data.get("twclid"),
            # wbraid=data.get("wbraid"),
            # gbraid=data.get("gbraid"),
            # utm_campaign=data.get("utm_campaign"),
            # utm_source=data.get("utm_source"),
            # utm_medium=data.get("utm_medium"),
            # utm_term=data.get("utm_term"),
            # utm_content=data.get("utm_content"),
            # other_utm_params=data.get("other_utm_params"),
        )


@dataclass(kw_only=True)
class TargetProperties:
    type: str | None
    id: str | None
    content: str | None
    attributes: dict[str, str | None] | None

    @classmethod
    def from_api_payload(cls, data: dict[str, Any]) -> Self:
        return cls(
            type=data.get("type"),
            id=data.get("id"),
            content=data.get("content"),
            attributes=data.get("attributes"),
        )


@dataclass(kw_only=True)
class CorrelationContext:
    session: SessionProperties | None
    traffic_source: TrafficSourceProperties | None
    account_id: str | None
    visitor_id: str | None

    @classmethod
    def from_api_payload(cls, data: dict[str, str]) -> Self:
        session: SessionProperties | None = None
        traffic_source: TrafficSourceProperties | None = None
        account_id: str | None = None
        visitor_id: str | None = None

        if (v := data.get(f"{EAVE_COLLECTOR_COOKIE_PREFIX}traffic_source")) and isinstance(v, str):
            try:
                us = json.loads(v)
                traffic_source = TrafficSourceProperties.from_api_payload(us)
            except Exception as e:
                # Catch JSON parse error
                LOGGER.exception(e)

        if (v := data.get(f"{EAVE_COLLECTOR_COOKIE_PREFIX}session")) and isinstance(v, str):
            try:
                us = json.loads(v)
                session = SessionProperties.from_api_payload(us)
            except Exception as e:
                # Catch JSON parse error
                LOGGER.exception(e)

        if (v := data.get(f"{EAVE_COLLECTOR_COOKIE_PREFIX}account_id")) and isinstance(v, str):
            account_id = v

        if (v := data.get(f"{EAVE_COLLECTOR_COOKIE_PREFIX}visitor_id")) and isinstance(v, str):
            visitor_id = v

        return cls(
            session=session,
            traffic_source=traffic_source,
            account_id=account_id,
            visitor_id=visitor_id,
        )


@dataclass(kw_only=True)
class BrowserEventPayload:
    action: BrowserAction | None
    timestamp: float | None
    target: TargetProperties | None
    device: DeviceProperties | None
    current_page: CurrentPageProperties | None
    extra: dict[str, JsonScalar | None] | None
    corr_ctx: CorrelationContext | None
    # session: SessionProperties | None = None
    # user: UserProperties | None = None
    # traffic_source: TrafficSourceProperties | None = None

    @classmethod
    def from_api_payload(cls, data: dict[str, Any]) -> Self:
        return cls(
            action=BrowserAction.from_str(v) if (v := data.get("action")) else None,
            timestamp=data.get("timestamp"),
            target=TargetProperties.from_api_payload(v) if (v := data.get("target")) and isinstance(v, dict) else None,
            device=DeviceProperties.from_api_payload(v) if (v := data.get("device")) and isinstance(v, dict) else None,
            current_page=CurrentPageProperties.from_api_payload(v)
            if (v := data.get("current_page")) and isinstance(v, dict)
            else None,
            extra=data.get("extra"),
            corr_ctx=CorrelationContext.from_api_payload(v)
            if (v := data.get("corr_ctx")) and isinstance(v, dict)
            else None,
        )

        # if (v := data.get("session")) and isinstance(v, dict):
        #     self.session = SessionProperties(v)

        # if (v := data.get("user")) and isinstance(v, dict):
        #     self.user = UserProperties(v)

        # if (v := data.get("traffic_source")) and isinstance(v, dict):
        #     self.traffic_source = TrafficSourceProperties(v)
