import re
from typing import Any
from starlette.requests import Request

from starlette.responses import Response
from eave.stdlib.auth_cookies import delete_auth_cookies, get_auth_cookies, set_auth_cookies
from eave.stdlib.test_util import UtilityBaseTestCase


class AuthCookiesTestBase(UtilityBaseTestCase):
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

        self.data_account_id = self.anystr("account_id")
        self.data_team_id = self.anystr("team_id")
        self.data_access_token = self.anystr("access_token")


class AuthCookiesTest(AuthCookiesTestBase):
    async def test_set_auth_cookies_with_all_data(self):
        set_auth_cookies(
            response=self.mock_response,
            team_id=self.data_team_id,
            account_id=self.data_account_id,
            access_token=self.data_access_token,
        )
        cookies = [v for k, v in self.mock_response.headers.items() if k == "set-cookie"]

        assert len(cookies) == 2
        assert any(re.search(f"^ev_account_id={self.data_account_id};", v) for v in cookies)
        assert any(re.search(f"^ev_access_token={self.data_access_token};", v) for v in cookies)

    async def test_get_auth_cookies_with_all_data(self):
        cookies = get_auth_cookies(
            {
                "ev_account_id_202310": self.data_account_id,
                "ev_access_token_202310": self.data_access_token,
            }
        )

        assert cookies.account_id == self.data_account_id
        assert cookies.access_token == self.data_access_token

    async def test_get_auth_cookies_with_account_id_only(self):
        cookies = get_auth_cookies(
            {
                "ev_account_id_202310": self.data_account_id,
            }
        )

        assert cookies.account_id == self.data_account_id
        assert cookies.access_token is None

    async def test_get_auth_cookies_with_access_token_only(self):
        cookies = get_auth_cookies(
            {
                "ev_access_token_202310": self.data_access_token,
            }
        )

        assert cookies.account_id is None
        assert cookies.access_token == self.data_access_token

    async def test_get_auth_cookies_with_no_data(self):
        cookies = get_auth_cookies({})

        assert cookies.account_id is None
        assert cookies.access_token is None

    async def test_delete_auth_cookies(self):
        delete_auth_cookies(response=self.mock_response)
        cookies = [v for k, v in self.mock_response.headers.items() if k == "set-cookie"]
        assert len(cookies) == 2

        assert any(re.search('^ev_account_id="";', v) for v in cookies)
        assert any(re.search('^ev_access_token="";', v) for v in cookies)
