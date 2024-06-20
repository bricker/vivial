import json

from eave.collectors.core.correlation_context.base import EAVE_COLLECTOR_COOKIE_PREFIX
from eave.core.internal.atoms.api_types import (
    BrowserAction,
    BrowserEventPayload,
    CorrelationContext,
    CurrentPageProperties,
    DeviceBrandProperties,
    DeviceProperties,
    SessionProperties,
    TargetProperties,
    TrafficSourceProperties,
)
from eave.stdlib.logging import LogContext

from .base import BaseTestCase

empty_ctx = LogContext()


class TestAtomApiTypes(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_device_brand_properties(self) -> None:
        e = DeviceBrandProperties({})
        assert e.brand is None
        assert e.version is None

        e = DeviceBrandProperties(
            {
                "brand": self.anystr("device_brand.brand"),
                "version": self.anystr("device_brand.version"),
                self.anystr("unrecognized attribute"): self.anystr(),
            }
        )
        assert e.brand == self.getstr("device_brand.brand")
        assert e.version == self.getstr("device_brand.version")

    async def test_device_properties(self) -> None:
        e = DeviceProperties({})
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

        e = DeviceProperties(
            {
                "user_agent": self.anystr("device.user_agent"),
                "brands": [
                    {
                        "brand": self.anystr("device.brands[0].brand"),
                        "version": self.anystr("device.brands[0].version"),
                        self.anystr("unrecognized attribute 1"): self.anystr(),
                    }
                ],
                "platform": self.anystr("device.platform"),
                "mobile": self.anybool("device.mobile"),
                "form_factor": self.anystr("device.form_factor"),
                "model": self.anystr("device.model"),
                "platform_version": self.anystr("device.platform_version"),
                "screen_width": self.anyint("device.screen_width"),
                "screen_height": self.anyint("device.screen_height"),
                "screen_avail_width": self.anyint("device.screen_avail_width"),
                "screen_avail_height": self.anyint("device.screen_avail_height"),
                self.anystr("unrecognized attribute 2"): self.anystr(),
            }
        )
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

    async def test_current_page_properties(self):
        e = CurrentPageProperties({})
        assert e.url is None
        assert e.title is None
        assert e.pageview_id is None

        e = CurrentPageProperties(
            {
                "url": self.anyurl("current_page.url"),
                "title": self.anystr("current_page.title"),
                "pageview_id": self.anystr("current_page.pageview_id"),
                self.anystr("unrecognized attribute"): self.anystr(),
            }
        )
        assert e.url == self.geturl("current_page.url")
        assert e.title == self.getstr("current_page.title")
        assert e.pageview_id == self.getstr("current_page.pageview_id")

    async def test_session_properties(self):
        e = SessionProperties({})
        assert e.id is None
        assert e.start_timestamp is None

        e = SessionProperties(
            {
                "id": self.anystr("session.id"),
                "start_timestamp": self.anytime("session.start_timestamp"),
                self.anystr("unrecognized attribute"): self.anystr(),
            }
        )
        assert e.id == self.getstr("session.id")
        assert e.start_timestamp == self.gettime("session.start_timestamp")

    async def test_traffic_source_properties(self):
        e = TrafficSourceProperties({})
        assert e.timestamp is None
        assert e.browser_referrer is None
        assert e.tracking_params is None

        e = TrafficSourceProperties(
            {
                "timestamp": self.anytime("traffic_source.timestamp"),
                "browser_referrer": self.anystr("traffic_source.browser_referrer"),
                "tracking_params": self.anydict("traffic_source.tracking_params"),
                self.anystr("unrecognized attribute"): self.anystr(),
            }
        )
        assert e.timestamp == self.gettime("traffic_source.timestamp")
        assert e.browser_referrer == self.getstr("traffic_source.browser_referrer")
        assert e.tracking_params == self.getdict("traffic_source.tracking_params")

    async def test_target_properties(self):
        e = TargetProperties({})
        assert e.type is None
        assert e.id is None
        assert e.content is None
        assert e.attributes is None

        e = TargetProperties(
            {
                "type": self.anystr("target.type"),
                "id": self.anystr("target.id"),
                "content": self.anystr("target.content"),
                "attributes": self.anydict("target.attributes"),
                self.anystr("unrecognized attribute"): self.anystr(),
            }
        )
        assert e.type == self.getstr("target.type")
        assert e.id == self.getstr("target.id")
        assert e.content == self.getstr("target.content")
        assert e.attributes == self.getdict("target.attributes")

    async def test_correlation_context(self):
        e = CorrelationContext({})
        assert e.session is None
        assert e.traffic_source is None
        assert e.account_id is None
        assert e.visitor_id is None

        e = CorrelationContext(
            {
                f"{EAVE_COLLECTOR_COOKIE_PREFIX}session": json.dumps(
                    {
                        "id": self.anystr("corr_ctx.session.id"),
                        self.anystr("unrecognized attribute 1"): self.anystr(),
                    }
                ),
                f"{EAVE_COLLECTOR_COOKIE_PREFIX}traffic_source": json.dumps(
                    {
                        "browser_referrer": self.anystr("corr_ctx.traffic_source.browser_referrer"),
                        self.anystr("unrecognized attribute 2"): self.anystr(),
                    }
                ),
                f"{EAVE_COLLECTOR_COOKIE_PREFIX}account_id": self.anystr("corr_ctx.account_id"),
                f"{EAVE_COLLECTOR_COOKIE_PREFIX}visitor_id": self.anystr("corr_ctx.visitor_id"),
                self.anystr("unrecognized attribute 3"): self.anystr(),
            }
        )
        assert e.session is not None
        assert e.session.id == self.getstr("corr_ctx.session.id")
        assert e.traffic_source is not None
        assert e.traffic_source.browser_referrer == self.getstr("corr_ctx.traffic_source.browser_referrer")
        assert e.account_id == self.getstr("corr_ctx.account_id")
        assert e.visitor_id == self.getstr("corr_ctx.visitor_id")

        # test with JSON errors
        e = CorrelationContext(
            {
                f"{EAVE_COLLECTOR_COOKIE_PREFIX}session": self.anystr("bad json 1"),
                f"{EAVE_COLLECTOR_COOKIE_PREFIX}traffic_source": self.anystr("bad json 2"),
                f"{EAVE_COLLECTOR_COOKIE_PREFIX}account_id": self.anystr("corr_ctx.account_id 2"),
                f"{EAVE_COLLECTOR_COOKIE_PREFIX}visitor_id": self.anystr("corr_ctx.visitor_id 2"),
            }
        )
        assert e.session is None
        assert e.traffic_source is None
        assert e.account_id == self.getstr("corr_ctx.account_id 2")
        assert e.visitor_id == self.getstr("corr_ctx.visitor_id 2")

    async def test_browser_event_payload(self):
        e = BrowserEventPayload({})
        assert e.action is None
        assert e.timestamp is None
        assert e.target is None
        assert e.device is None
        assert e.current_page is None
        assert e.extra is None
        assert e.corr_ctx is None

        e = BrowserEventPayload(
            {
                "action": BrowserAction.CLICK,
                "timestamp": self.anytime("event.timestamp"),
                "target": {
                    "id": self.anystr("event.target.id"),
                    self.anystr("unrecognized attribute 1"): self.anystr(),
                },
                "device": {
                    "user_agent": self.anystr("event.device.user_agent"),
                    self.anystr("unrecognized attribute 2"): self.anystr(),
                },
                "current_page": {
                    "url": self.anyurl("event.current_page.url"),
                    self.anystr("unrecognized attribute 3"): self.anystr(),
                },
                "extra": self.anydict("event.extra"),
                "corr_ctx": {
                    f"{EAVE_COLLECTOR_COOKIE_PREFIX}account_id": self.anystr("event.corr_ctx.account_id"),
                    self.anystr("unrecognized attribute 4"): self.anystr(),
                },
                self.anystr("unrecognized attribute 5"): self.anystr(),
            }
        )
        assert e.action == BrowserAction.CLICK
        assert e.timestamp == self.gettime("event.timestamp")
        assert e.target is not None
        assert e.target.id == self.getstr("event.target.id")
        assert e.device is not None
        assert e.device.user_agent == self.getstr("event.device.user_agent")
        assert e.current_page is not None
        assert e.current_page.url == self.geturl("event.current_page.url")
        assert e.extra == self.getdict("event.extra")
        assert e.corr_ctx is not None
        assert e.corr_ctx.account_id == self.getstr("event.corr_ctx.account_id")

        # invalid action
        e = BrowserEventPayload(
            {
                "action": self.anystr("invalid action"),
            }
        )
        assert e.action is None
