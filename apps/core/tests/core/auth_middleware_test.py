import unittest.mock

from http import HTTPStatus
from eave.core.internal.oauth.google import GoogleOAuthV2GetResponse

from eave.core.internal.orm.account import AccountOrm
from eave.stdlib.core_api.models.account import AuthProvider

from .base import BaseTestCase
import google.oauth2.credentials
from eave.stdlib.auth_cookies import (
    EAVE_TEAM_ID_COOKIE_NAME,
    EAVE_ACCOUNT_ID_COOKIE_NAME,
    EAVE_ACCESS_TOKEN_COOKIE_NAME,
)


class TestAuthenticationMiddlewareBase(BaseTestCase):
    _eave_account: AccountOrm

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        async with self.db_session.begin() as s:
            self._eave_account = await self.make_account(s, auth_provider=AuthProvider.google)

        self._google_userinfo_response = GoogleOAuthV2GetResponse(
            email=self.anystr("google.email"),
            family_name=self.anystr("google.family_name"),
            gender=self.anystr("google.gender"),
            given_name=self.anystr("google.given_name"),
            hd=self.anystr("google.hd"),
            id=self.anystr("google.id"),
            link=self.anystr("google.link"),
            locale=self.anystr("google.locale"),
            name=self.anystr("google.name"),
            picture=self.anystr("google.picture"),
            verified_email=True,
        )

        self._get_userinfo_mock = self.patch(patch=unittest.mock.patch("eave.core.internal.oauth.google.get_userinfo"))

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
            account_id=None,
            access_token=None,
        )

        assert response.status_code == HTTPStatus.OK

    async def test_not_required_auth_provided(self) -> None:
        response = await self.make_request(
            method="GET",
            path="/status",
            account_id=self.anyuuid(),
            access_token=self.anystr(),
        )

        assert response.status_code == HTTPStatus.OK


class TestAuthenticationMiddlewareRequiredInvalidRequest(TestAuthenticationMiddlewareBase):
    async def test_required_missing_account_id_header(self) -> None:
        response = await self.make_request(
            path="/me/query",
            account_id=None,
            access_token=self._eave_account.access_token,
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_required_missing_access_token_header(self) -> None:
        response = await self.make_request(
            path="/me/query",
            account_id=self._eave_account.id,
            access_token=None,
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_required_missing_all(self) -> None:
        response = await self.make_request(
            path="/me/query",
            account_id=None,
            access_token=None,
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_required_invalid_account_id(self) -> None:
        response = await self.make_request(
            path="/me/query",
            account_id=self.anyuuid(),
            access_token=self._eave_account.access_token,
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) is None
        assert response.cookies.get(EAVE_TEAM_ID_COOKIE_NAME) is None
        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) is None

    async def test_required_invalid_access_token(self) -> None:
        response = await self.make_request(
            path="/me/query", account_id=self._eave_account.id, access_token=self.anystr()
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) is None
        assert response.cookies.get(EAVE_TEAM_ID_COOKIE_NAME) is None
        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) is None


class TestAuthenticationMiddlewareRequiredValidRequest(TestAuthenticationMiddlewareBase):
    async def test_required_valid_auth_headers(self) -> None:
        response = await self.make_request(
            path="/me/query",
            team_id=self._eave_account.team_id,
            account_id=self._eave_account.id,
            access_token=self._eave_account.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) == str(self._eave_account.id)
        assert response.cookies.get(EAVE_TEAM_ID_COOKIE_NAME) == str(self._eave_account.team_id)
        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == self._eave_account.access_token

    async def test_previous_access_token_accepted(self) -> None:
        async with self.db_session.begin() as s:
            self._eave_account.access_token = self.anystr("current_token")
            self._eave_account.previous_access_token = self.anystr("previous_token")
            await self.save(s, self._eave_account)

        response = await self.make_request(
            path="/me/query",
            team_id=self._eave_account.team_id,
            account_id=self._eave_account.id,
            access_token=self.getstr("previous_token"),
        )

        assert response.status_code == HTTPStatus.OK
        assert self._eave_account.access_token == self.getstr("current_token")
        assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) == str(self._eave_account.id)
        assert response.cookies.get(EAVE_TEAM_ID_COOKIE_NAME) == str(self._eave_account.team_id)
        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == self.getstr("current_token")

    async def test_access_token_not_refreshed(self) -> None:
        self._get_userinfo_mock.side_effect = self._mock_get_userinfo_token_not_refreshed

        response = await self.make_request(
            path="/me/query",
            team_id=self._eave_account.team_id,
            account_id=self._eave_account.id,
            access_token=self._eave_account.access_token,
        )

        async with self.db_session.begin() as s:
            eave_account = await self.reload(s, obj=self._eave_account)
            assert eave_account

        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == self.getstr("account.oauth_token")
        assert eave_account.access_token == self.getstr("account.oauth_token")

    async def test_access_token_refreshed(self) -> None:
        self._get_userinfo_mock.side_effect = self._mock_get_userinfo_token_refreshed

        response = await self.make_request(
            path="/me/query",
            team_id=self._eave_account.team_id,
            account_id=self._eave_account.id,
            access_token=self._eave_account.access_token,
        )

        async with self.db_session.begin() as s:
            eave_account = await self.reload(s, obj=self._eave_account)
            assert eave_account

        assert eave_account.access_token == self.getstr("refreshed_token")
        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == self.getstr("refreshed_token")
