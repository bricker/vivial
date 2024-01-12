import re
from typing import Any
from starlette.requests import Request
import aiohttp

from starlette.responses import Response
from eave.stdlib.test_util import UtilityBaseTestCase
from eave.stdlib.utm_cookies import (
    EAVE_COOKIE_PREFIX_UTM,
    EAVE_VISITOR_ID_COOKIE_NAME,
    TrackingParam,
    get_tracking_cookies,
    set_tracking_cookies,
)


class UtmCookiesTestBase(UtilityBaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        # https://asgi.readthedocs.io/en/latest/specs/www.html#http-connection-scope
        self.mock_scope: dict[str, Any] = {
            "type": "http",
            "headers": [],
            "path": "",
            "method": "GET",
            "http_version": "1.1",
        }
        self.mock_request = Request(scope=self.mock_scope)
        self.mock_response = Response()

        self.data_campaign = self.anystr("campaign")
        self.data_term = self.anystr("term")
        self.data_gclid = self.anystr("gclid")
        self.data_visitor_id = self.anystr("visitor_id")
        self.data_ignored_param = self.anystr("ignored_param")

        self.mock_scope[
            "query_string"
        ] = f"utm_campaign={self.data_campaign}&UTM_TERM={self.data_term}&gclid={self.data_gclid}&ignored_param={self.data_ignored_param}"


class UtmCookiesTest(UtmCookiesTestBase):
    async def test_constants(self):
        # These cannot be changed, because the names are hardcoded in GTM. Changing these will break tracking.
        assert EAVE_COOKIE_PREFIX_UTM == "ev_utm_"
        assert EAVE_VISITOR_ID_COOKIE_NAME == "ev_visitor_id"

        assert TrackingParam.gclid == "gclid"
        assert TrackingParam.msclkid == "msclkid"
        assert TrackingParam.fbclid == "fbclid"
        assert TrackingParam.twclid == "twclid"
        assert TrackingParam.li_fat_id == "li_fat_id"
        assert TrackingParam.rdt_cid == "rdt_cid"
        assert TrackingParam.ttclid == "ttclid"
        assert TrackingParam.keyword == "keyword"
        assert TrackingParam.matchtype == "matchtype"
        assert TrackingParam.campaign == "campaign"
        assert TrackingParam.campaign_id == "campaign_id"
        assert TrackingParam.pid == "pid"
        assert TrackingParam.cid == "cid"

    async def test_set_cookies_visitor_id_not_set(self):
        set_tracking_cookies(
            request=self.mock_request,
            response=self.mock_response,
        )
        cookies = [v for k, v in self.mock_response.headers.items() if k == aiohttp.hdrs.SET_COOKIE]

        assert len(cookies) == 4  # The fourth is visitor_id

        assert any(re.search(f"^{EAVE_COOKIE_PREFIX_UTM}utm_campaign={self.data_campaign};", v) for v in cookies)
        assert any(re.search(f"^{EAVE_COOKIE_PREFIX_UTM}utm_term={self.data_term};", v) for v in cookies)
        assert any(re.search(f"^{EAVE_COOKIE_PREFIX_UTM}gclid={self.data_gclid};", v) for v in cookies)
        assert any(
            re.search(f"^{EAVE_VISITOR_ID_COOKIE_NAME}=", v) for v in cookies
        )  # value is generated internal to function
        assert not any(re.search("ignored_param", v) for v in cookies)

    async def test_set_cookies_visitor_id_already_set(self):
        self.mock_request.cookies.update({EAVE_VISITOR_ID_COOKIE_NAME: self.data_visitor_id})

        set_tracking_cookies(
            request=self.mock_request,
            response=self.mock_response,
        )
        cookies = [v for k, v in self.mock_response.headers.items() if k == aiohttp.hdrs.SET_COOKIE]
        assert len(cookies) == 3

        assert not any(re.search(f"^{EAVE_VISITOR_ID_COOKIE_NAME}", v) for v in cookies)
        assert any(re.search(f"{EAVE_COOKIE_PREFIX_UTM}utm_campaign", v) for v in cookies)

    async def test_set_cookies_case_agnostic(self):
        self.mock_scope["query_string"] = f"utm_campaign={self.data_campaign}&UTM_TERM={self.data_term}"

        set_tracking_cookies(
            request=self.mock_request,
            response=self.mock_response,
        )
        cookies = [v for k, v in self.mock_response.headers.items() if k == aiohttp.hdrs.SET_COOKIE]
        assert any(re.search(f"^{EAVE_COOKIE_PREFIX_UTM}utm_campaign={self.data_campaign};", v) for v in cookies)
        assert any(re.search(f"^{EAVE_COOKIE_PREFIX_UTM}utm_term={self.data_term}", v) for v in cookies)

    async def test_get_tracking_cookies_with_visitor_id(self):
        self.mock_request.cookies.update(
            {
                EAVE_VISITOR_ID_COOKIE_NAME: self.data_visitor_id,
                "ignored_param": self.anystr(),
                f"{EAVE_COOKIE_PREFIX_UTM}utm_campaign": self.data_campaign,
                f"{EAVE_COOKIE_PREFIX_UTM}gclid": self.data_gclid,
            }
        )
        cookies = get_tracking_cookies(request=self.mock_request)

        assert cookies.visitor_id == self.data_visitor_id
        assert cookies.utm_params.get("utm_campaign") == self.data_campaign
        assert cookies.utm_params.get("gclid") == self.data_gclid
        assert cookies.utm_params.get("ignored_param") is None

    async def test_get_tracking_cookies_without_visitor_id(self):
        self.mock_request.cookies.update(
            {
                # ev_visitor_id not set
                f"{EAVE_COOKIE_PREFIX_UTM}utm_campaign": self.data_campaign,
            }
        )
        cookies = get_tracking_cookies(request=self.mock_request)
        assert cookies.visitor_id is None
