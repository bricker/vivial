import re
from typing import Any, override

import aiohttp
from starlette.requests import Request
from starlette.responses import Response

from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.cookies import delete_http_cookie, set_http_cookie
from eave.stdlib.util import istr_eq

from .base import StdlibBaseTestCase


class CookiesTestBase(StdlibBaseTestCase):
    @override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        # https://asgi.readthedocs.io/en/latest/specs/www.html#http-connection-scope
        self.mock_scope: dict[str, Any] = {  # pyright: ignore [reportUninitializedInstanceVariable]
            "type": "http",
            "headers": [],
            "path": "",
            "method": "GET",
            "http_version": "1.1",
        }
        self.mock_request = Request(scope=self.mock_scope)  # pyright: ignore [reportUninitializedInstanceVariable]
        self.mock_response = Response()  # pyright: ignore [reportUninitializedInstanceVariable]


class CookiesTest(CookiesTestBase):
    async def test_set_http_cookie(self):
        key = self.anystr("cookie_key")
        value = self.anystr("cookie_value")
        set_http_cookie(key=key, value=value, response=self.mock_response)
        cookies = [v for k, v in self.mock_response.headers.items() if istr_eq(k, aiohttp.hdrs.SET_COOKIE)]

        assert len(cookies) == 1

        cookie = next((v for v in cookies if re.search(f"^{key}={value}", v)), None)
        assert cookie
        assert re.search(f"Domain={SHARED_CONFIG.eave_hostname_public}", cookie)
        assert re.search("HttpOnly", cookie, flags=re.IGNORECASE)

    async def test_set_http_cookie_with_samesite_none(self):
        key = self.anystr("cookie_key")
        value = self.anystr("cookie_value")
        set_http_cookie(key=key, value=value, response=self.mock_response, samesite="none")
        cookies = [v for k, v in self.mock_response.headers.items() if istr_eq(k, aiohttp.hdrs.SET_COOKIE)]

        assert len(cookies) == 1

        cookie = next((v for v in cookies if re.search(f"^{key}={value}", v)), None)
        assert cookie
        assert re.search("SameSite=None", cookie, flags=re.IGNORECASE)
        assert re.search("Secure", cookie, flags=re.IGNORECASE)

    async def test_set_http_cookie_with_domain(self):
        key = self.anystr("cookie_key")
        value = self.anystr("cookie_value")
        set_http_cookie(key=key, value=value, response=self.mock_response, domain="example.com")
        cookies = [v for k, v in self.mock_response.headers.items() if istr_eq(k, aiohttp.hdrs.SET_COOKIE)]

        assert len(cookies) == 1

        cookie = next((v for v in cookies if re.search(f"^{key}={value}", v)), None)
        assert cookie
        assert re.search("Domain=example.com", cookie)

    async def test_delete_http_cookie(self):
        key = self.anystr("cookie_key")
        delete_http_cookie(key=key, response=self.mock_response)
        cookies = [v for k, v in self.mock_response.headers.items() if istr_eq(k, aiohttp.hdrs.SET_COOKIE)]

        assert len(cookies) == 1

        cookie = next((v for v in cookies if re.search(f'^{key}=""', v)), None)
        assert cookie
        assert re.search(f"Domain={SHARED_CONFIG.eave_hostname_public}", cookie)
        assert re.search("HttpOnly", cookie, flags=re.IGNORECASE)

    async def test_set_analytics_cookie(self):
        key = self.anystr("cookie_key")
        value = self.anystr("cookie_value")
        set_http_cookie(key=key, value=value, response=self.mock_response)
        cookies = [v for k, v in self.mock_response.headers.items() if istr_eq(k, aiohttp.hdrs.SET_COOKIE)]

        assert len(cookies) == 1

        cookie = next((v for v in cookies if re.search(f"^{key}={value}", v)), None)
        assert cookie
        assert re.search(f"Domain={SHARED_CONFIG.eave_hostname_public}", cookie)

    async def test_delete_analytics_cookie(self):
        key = self.anystr("cookie_key")
        delete_http_cookie(key=key, response=self.mock_response)
        cookies = [v for k, v in self.mock_response.headers.items() if istr_eq(k, aiohttp.hdrs.SET_COOKIE)]

        assert len(cookies) == 1

        cookie = next((v for v in cookies if re.search(f'^{key}=""', v)), None)
        assert cookie
        assert re.search(f"Domain={SHARED_CONFIG.eave_hostname_public}", cookie)
