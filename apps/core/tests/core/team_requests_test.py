from http import HTTPStatus
from eave.core.internal.orm.atlassian_installation import AtlassianInstallationOrm
from eave.core.internal.orm.slack_installation import SlackInstallationOrm

from eave.stdlib.core_api.operations.team import GetTeam

from .base import BaseTestCase


class TestTeamRequests(BaseTestCase):
    async def test_get_team_with_integrations(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            await SlackInstallationOrm.create(
                session=s,
                team_id=team.id,
                bot_refresh_token=self.anystring("bot_refresh_token"),
                bot_token=self.anystring("bot_token"),
                slack_team_id=self.anystring("slack_team_id"),
                bot_token_exp=self.anydatetime("bot_token_exp", future=True),
            )
            await AtlassianInstallationOrm.create(
                session=s,
                team_id=team.id,
                confluence_space_key=self.anystring("confluence_space"),
                atlassian_cloud_id=self.anystring("atlassian_cloud_id"),
                oauth_token_encoded=self.anyjson("oauth_token_encoded"),
            )

        response = await self.make_request(
            path="/team/query",
            payload=None,
            team_id=team.id,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetTeam.ResponseBody(**response.json())

        assert response_obj.integrations.slack_integration is not None
        assert response_obj.integrations.slack_integration.slack_team_id == self.anystring("slack_team_id")
        assert response_obj.integrations.slack_integration.bot_token == self.anystring("bot_token")

        assert response_obj.integrations.atlassian_integration is not None
        assert response_obj.integrations.atlassian_integration.confluence_space_key == self.anystring("confluence_space")
        assert response_obj.integrations.atlassian_integration.atlassian_cloud_id == self.anystring("atlassian_cloud_id")
        assert response_obj.integrations.atlassian_integration.oauth_token_encoded == self.anyjson("oauth_token_encoded")

    async def test_get_team_without_integrations(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

        response = await self.make_request(
            path="/team/query",
            payload=None,
            team_id=team.id,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetTeam.ResponseBody(**response.json())
        assert response_obj.team.id == team.id
