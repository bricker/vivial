from http import HTTPStatus

from eave.stdlib.core_api.operations.team import GetMyTeamRequest

from .base import BaseTestCase


class TestTeamRequests(BaseTestCase):
    async def test_get_team(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

        response = await self.make_request(
            path=GetMyTeamRequest.config.path,
            payload=None,
            team_id=team.id,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetMyTeamRequest.ResponseBody(**response.json())
        assert response_obj.team.id == team.id
