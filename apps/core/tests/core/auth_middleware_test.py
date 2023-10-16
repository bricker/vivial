from http import HTTPStatus

from eave.core.internal.orm.account import AccountOrm

from .base import BaseTestCase


class TestAuthenticationMiddlewareBase(BaseTestCase):
    _eave_account: AccountOrm

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        async with self.db_session.begin() as s:
            self._eave_account = await self.make_account(s)


class TestAuthenticationMiddlewareRequired(TestAuthenticationMiddlewareBase):
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
        assert response.cookies.get("ev_account_id_202310") is None
        assert response.cookies.get("ev_team_id_202310") is None
        assert response.cookies.get("ev_access_token_202310") is None

    async def test_required_invalid_access_token(self) -> None:
        response = await self.make_request(
            path="/me/query", account_id=self._eave_account.id, access_token=self.anystr()
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.cookies.get("ev_account_id_202310") is None
        assert response.cookies.get("ev_team_id_202310") is None
        assert response.cookies.get("ev_access_token_202310") is None

    async def test_required_valid_auth_headers(self) -> None:
        response = await self.make_request(
            path="/me/query",
            team_id=self._eave_account.team_id,
            account_id=self._eave_account.id,
            access_token=self._eave_account.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        assert response.cookies.get("ev_account_id_202310") == str(self._eave_account.id)
        assert response.cookies.get("ev_team_id_202310") == str(self._eave_account.team_id)
        assert response.cookies.get("ev_access_token_202310") == self.b64encode(
            self._eave_account.access_token, urlsafe=False
        )

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
        assert response.cookies.get("ev_account_id_202310") == str(self._eave_account.id)
        assert response.cookies.get("ev_team_id_202310") == str(self._eave_account.team_id)
        assert response.cookies.get("ev_access_token_202310") == self.b64encode(
            self.getstr("current_token"), urlsafe=False
        )
