import re
from typing import Any
from starlette.requests import Request

from starlette.responses import Response
from eave.stdlib.cookies import delete_http_cookie, set_http_cookie
from eave.stdlib.test_util import UtilityBaseTestCase


class CookiesTestBase(UtilityBaseTestCase):
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


class CookiesTest(CookiesTestBase):
    async def test_set_http_cookie(self):
        key = self.anystr("cookie_key")
        value = self.anystr("cookie_value")
        set_http_cookie(key=key, value=value, response=self.mock_response)
        cookies = [v for k, v in self.mock_response.headers.items() if k == "set-cookie"]

        assert len(cookies) == 1

        cookie = next((v for v in cookies if re.search(f"^{key}={value}", v)), None)
        assert cookie
        assert re.search("Domain=.eave.run;", cookie)
        assert re.search("HttpOnly;", cookie)

    async def test_delete_http_cookie(self):
        key = self.anystr("cookie_key")
        delete_http_cookie(key=key, response=self.mock_response)
        cookies = [v for k, v in self.mock_response.headers.items() if k == "set-cookie"]

        assert len(cookies) == 1

        cookie = next((v for v in cookies if re.search(f'^{key}=""', v)), None)
        assert cookie
        assert re.search("Domain=.eave.run;", cookie)
        assert re.search("HttpOnly;", cookie)

    async def test_set_analytics_cookie(self):
        key = self.anystr("cookie_key")
        value = self.anystr("cookie_value")
        set_http_cookie(key=key, value=value, response=self.mock_response)
        cookies = [v for k, v in self.mock_response.headers.items() if k == "set-cookie"]

        assert len(cookies) == 1

        cookie = next((v for v in cookies if re.search(f"^{key}={value}", v)), None)
        assert cookie
        assert re.search("Domain=.eave.run;", cookie)

    async def test_delete_analytics_cookie(self):
        key = self.anystr("cookie_key")
        delete_http_cookie(key=key, response=self.mock_response)
        cookies = [v for k, v in self.mock_response.headers.items() if k == "set-cookie"]

        assert len(cookies) == 1

        cookie = next((v for v in cookies if re.search(f'^{key}=""', v)), None)
        assert cookie
        assert re.search("Domain=.eave.run;", cookie)
