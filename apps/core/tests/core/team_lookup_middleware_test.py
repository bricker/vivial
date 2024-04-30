from http import HTTPStatus

from aiohttp.hdrs import AUTHORIZATION

from eave.stdlib.auth_cookies import EAVE_TEAM_ID_COOKIE_NAME
from eave.stdlib.core_api.operations.status import Status
from eave.stdlib.core_api.operations.team import GetTeamRequest
from eave.stdlib.headers import EAVE_ACCOUNT_ID_HEADER, EAVE_TEAM_ID_HEADER

from .base import BaseTestCase


class TestTeamLookupMiddleware(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        async with self.db_session.begin() as s:
            self._team = await self.make_team(session=s)
            self._account = await self.make_account(session=s, team_id=self._team.id)

    async def test_team_id_bypass(self) -> None:
        response = await self.make_request(
            method=Status.config.method,
            path=Status.config.path,
            headers={EAVE_TEAM_ID_HEADER: None},
        )

        assert response.status_code == HTTPStatus.OK

    async def test_missing_team_id_header(self) -> None:
        response = await self.make_request(
            path=GetTeamRequest.config.path,
            headers={
                EAVE_TEAM_ID_HEADER: None,
                EAVE_ACCOUNT_ID_HEADER: str(self._account.id),
                AUTHORIZATION: f"Bearer {self._account.access_token}",
            },
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    async def test_invalid_team_id(self) -> None:
        response = await self.make_request(
            path=GetTeamRequest.config.path,
            headers={
                EAVE_TEAM_ID_HEADER: str(self.anyuuid()),
                EAVE_ACCOUNT_ID_HEADER: str(self._account.id),
                AUTHORIZATION: f"Bearer {self._account.access_token}",
            },
        )

        assert response.status_code == HTTPStatus.NOT_FOUND

    async def test_valid_team_id(self) -> None:
        response = await self.make_request(
            path=GetTeamRequest.config.path,
            headers={
                EAVE_TEAM_ID_HEADER: str(self._team.id),
                EAVE_ACCOUNT_ID_HEADER: str(self._account.id),
                AUTHORIZATION: f"Bearer {self._account.access_token}",
            },
        )

        assert response.status_code == HTTPStatus.OK

    async def test_valid_team_id_cookie(self) -> None:
        response = await self.make_request(
            path=GetTeamRequest.config.path,
            headers={
                EAVE_ACCOUNT_ID_HEADER: str(self._account.id),
                AUTHORIZATION: f"Bearer {self._account.access_token}",
            },
            cookies={EAVE_TEAM_ID_COOKIE_NAME: str(self._team.id)},
        )

        assert response.status_code == HTTPStatus.OK

    async def test_team_id_header_precedence(self) -> None:
        response = await self.make_request(
            path=GetTeamRequest.config.path,
            headers={
                EAVE_TEAM_ID_HEADER: str(self._team.id),
                EAVE_ACCOUNT_ID_HEADER: str(self._account.id),
                AUTHORIZATION: f"Bearer {self._account.access_token}",
            },
            cookies={EAVE_TEAM_ID_COOKIE_NAME: self.anystr()},
        )

        assert response.status_code == HTTPStatus.OK
