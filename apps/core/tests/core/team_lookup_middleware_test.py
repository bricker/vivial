from http import HTTPStatus
from eave.stdlib.core_api.operations.status import Status

from eave.stdlib.core_api.operations.team import GetTeamRequest
from eave.stdlib.headers import EAVE_TEAM_ID_HEADER

from .base import BaseTestCase


class TestTeamLookupMiddleware(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        async with self.db_session.begin() as s:
            self._team = await self.make_team(session=s)

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
            },
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST

    async def test_invalid_team_id(self) -> None:
        response = await self.make_request(
            path=GetTeamRequest.config.path,
            headers={
                EAVE_TEAM_ID_HEADER: str(self.anyuuid()),
            },
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
