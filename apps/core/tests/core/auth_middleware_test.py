import unittest.mock
from http import HTTPStatus

import google.oauth2.credentials
from aiohttp.hdrs import AUTHORIZATION

from eave.core.internal.oauth.google import GoogleOAuthV2GetResponse
from eave.core.internal.orm.account import AccountOrm
from eave.stdlib.auth_cookies import (
    EAVE_ACCESS_TOKEN_COOKIE_NAME,
    EAVE_ACCOUNT_ID_COOKIE_NAME,
)
from eave.stdlib.core_api.models.account import AuthProvider
from eave.stdlib.core_api.operations.account import GetMyAccountRequest
from eave.stdlib.headers import EAVE_ACCOUNT_ID_HEADER, EAVE_TEAM_ID_HEADER

from .base import BaseTestCase


class TestAuthenticationMiddlewareBase(BaseTestCase):
    _eave_account: AccountOrm

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        async with self.db_session.begin() as s:
            self._eave_account = await self.make_account(s, auth_provider=AuthProvider.google)

    def _mock_get_userinfo_token_refreshed(
        self, credentials: google.oauth2.credentials.Credentials
    ) -> GoogleOAuthV2GetResponse:
        credentials.token = self.anystr("refreshed_token")
        return self._google_userinfo_response

    def _mock_get_userinfo_token_not_refreshed(
        self, credentials: google.oauth2.credentials.Credentials
    ) -> GoogleOAuthV2GetResponse:
        return self._google_userinfo_response


class TestAuthenticationMiddlewareNotRequired(TestAuthenticationMiddlewareBase):
    async def test_not_required_missing_all(self) -> None:
        response = await self.make_request(
            method="GET",
            path="/status",
            headers={
                EAVE_ACCOUNT_ID_HEADER: None,
                AUTHORIZATION: None,
            },
        )

        assert response.status_code == HTTPStatus.OK

    async def test_not_required_auth_provided(self) -> None:
        response = await self.make_request(
            method="GET",
            path="/status",
            headers={
                EAVE_ACCOUNT_ID_HEADER: str(self.anyuuid()),
                AUTHORIZATION: f"Bearer {self.anystr()}",
            },
        )

        assert response.status_code == HTTPStatus.OK


class TestAuthenticationMiddlewareRequiredInvalidRequest(TestAuthenticationMiddlewareBase):
    async def test_required_missing_account_id_header(self) -> None:
        response = await self.make_request(
            path=GetMyAccountRequest.config.path,
            headers={
                EAVE_ACCOUNT_ID_HEADER: None,
                AUTHORIZATION: f"Bearer {self._eave_account.access_token}",
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_required_missing_access_token_header(self) -> None:
        response = await self.make_request(
            path=GetMyAccountRequest.config.path,
            headers={
                EAVE_ACCOUNT_ID_HEADER: str(self._eave_account.id),
                AUTHORIZATION: None,
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_required_missing_all(self) -> None:
        response = await self.make_request(
            path=GetMyAccountRequest.config.path,
            headers={
                EAVE_ACCOUNT_ID_HEADER: None,
                AUTHORIZATION: None,
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_required_invalid_account_id(self) -> None:
        response = await self.make_request(
            path=GetMyAccountRequest.config.path,
            headers={
                EAVE_ACCOUNT_ID_HEADER: str(self.anyuuid()),
                AUTHORIZATION: f"Bearer {self._eave_account.access_token}",
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) is None
        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) is None

    async def test_required_invalid_access_token(self) -> None:
        response = await self.make_request(
            path=GetMyAccountRequest.config.path, account_id=self._eave_account.id, access_token=self.anystr()
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) is None
        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) is None


class TestAuthenticationMiddlewareRequiredValidRequest(TestAuthenticationMiddlewareBase):
    async def test_required_valid_auth_headers(self) -> None:
        response = await self.make_request(
            path=GetMyAccountRequest.config.path,
            headers={
                EAVE_TEAM_ID_HEADER: str(self._eave_account.team_id),
                EAVE_ACCOUNT_ID_HEADER: str(self._eave_account.id),
                AUTHORIZATION: f"Bearer {self._eave_account.access_token}",
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) is None
        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == self._eave_account.access_token

    async def test_previous_access_token_accepted(self) -> None:
        async with self.db_session.begin() as s:
            self._eave_account.access_token = self.anystr("current_token")
            self._eave_account.previous_access_token = self.anystr("previous_token")
            await self.save(s, self._eave_account)

        response = await self.make_request(
            path=GetMyAccountRequest.config.path,
            headers={
                EAVE_TEAM_ID_HEADER: str(self._eave_account.team_id),
                EAVE_ACCOUNT_ID_HEADER: str(self._eave_account.id),
                AUTHORIZATION: f"Bearer {self.getstr("previous_token")}",
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert self._eave_account.access_token == self.getstr("current_token")
        assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) is None
        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == self.getstr("current_token")

    async def test_access_token_not_refreshed(self) -> None:
        self.get_mock("google_get_userinfo").side_effect = self._mock_get_userinfo_token_not_refreshed

        access_token_before = self._eave_account.access_token

        response = await self.make_request(
            path=GetMyAccountRequest.config.path,
            headers={
                EAVE_TEAM_ID_HEADER: str(self._eave_account.team_id),
                EAVE_ACCOUNT_ID_HEADER: str(self._eave_account.id),
                AUTHORIZATION: f"Bearer {self._eave_account.access_token}",
            },
        )

        async with self.db_session.begin() as s:
            eave_account = await self.reload(s, obj=self._eave_account)
            assert eave_account

        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == access_token_before
        assert eave_account.access_token == access_token_before

    async def test_access_token_refreshed(self) -> None:
        self.get_mock("google_get_userinfo").side_effect = self._mock_get_userinfo_token_refreshed

        response = await self.make_request(
            path=GetMyAccountRequest.config.path,
            headers={
                EAVE_TEAM_ID_HEADER: str(self._eave_account.team_id),
                EAVE_ACCOUNT_ID_HEADER: str(self._eave_account.id),
                AUTHORIZATION: f"Bearer {self._eave_account.access_token}",
            },
        )

        async with self.db_session.begin() as s:
            eave_account = await self.reload(s, obj=self._eave_account)
            assert eave_account

        assert eave_account.access_token == self.getstr("refreshed_token")
        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == self.getstr("refreshed_token")


class TestAuthenticationMiddlewareWithCookies(TestAuthenticationMiddlewareBase):
    async def test_valid_auth_with_cookies(self) -> None:
        response = await self.make_request(
            path=GetMyAccountRequest.config.path,
            cookies={
                EAVE_ACCOUNT_ID_COOKIE_NAME: str(self._eave_account.id),
                EAVE_ACCESS_TOKEN_COOKIE_NAME: str(self._eave_account.access_token),
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) is None
        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == self._eave_account.access_token

    async def test_auth_header_precedence(self) -> None:
        response = await self.make_request(
            path=GetMyAccountRequest.config.path,
            cookies={
                EAVE_ACCOUNT_ID_COOKIE_NAME: self.anystr("invalid account id"),
                EAVE_ACCESS_TOKEN_COOKIE_NAME: self.anystr("invalid access token"),
            },
            headers={
                EAVE_TEAM_ID_HEADER: str(self._eave_account.team_id),
                EAVE_ACCOUNT_ID_HEADER: str(self._eave_account.id),
                AUTHORIZATION: f"Bearer {self._eave_account.access_token}",
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) is None
        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == self._eave_account.access_token

    async def test_access_token_not_refreshed(self) -> None:
        self.get_mock("google_get_userinfo").side_effect = self._mock_get_userinfo_token_not_refreshed

        access_token_before = self._eave_account.access_token

        response = await self.make_request(
            path=GetMyAccountRequest.config.path,
            cookies={
                EAVE_ACCOUNT_ID_COOKIE_NAME: str(self._eave_account.id),
                EAVE_ACCESS_TOKEN_COOKIE_NAME: str(self._eave_account.access_token),
            },
        )

        async with self.db_session.begin() as s:
            eave_account = await self.reload(s, obj=self._eave_account)
            assert eave_account

        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == access_token_before
        assert eave_account.access_token == access_token_before

    async def test_access_token_refreshed(self) -> None:
        self.get_mock("google_get_userinfo").side_effect = self._mock_get_userinfo_token_refreshed

        response = await self.make_request(
            path=GetMyAccountRequest.config.path,
            cookies={
                EAVE_ACCOUNT_ID_COOKIE_NAME: str(self._eave_account.id),
                EAVE_ACCESS_TOKEN_COOKIE_NAME: str(self._eave_account.access_token),
            },
        )

        async with self.db_session.begin() as s:
            eave_account = await self.reload(s, obj=self._eave_account)
            assert eave_account

        assert eave_account.access_token == self.getstr("refreshed_token")
        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == self.getstr("refreshed_token")
