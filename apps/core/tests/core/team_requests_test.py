from http import HTTPStatus

import eave.stdlib.core_api.operations as eave_ops

import eave.core.internal.database as eave_db
import eave.core.internal.oauth.slack
import eave.core.internal.orm.atlassian_installation
import eave.core.internal.orm.slack_installation
import eave.core.internal.orm.team

from .base import BaseTestCase


class TestTeamRequests(BaseTestCase):
    async def test_get_team_with_integrations(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            await eave.core.internal.orm.slack_installation.SlackInstallationOrm.create(
                session=s,
                team_id=team.id,
                bot_refresh_token=self.anystring("bot_refresh_token"),
                bot_token=self.anystring("bot_token"),
                slack_team_id=self.anystring("slack_team_id"),
                bot_token_exp=self.anydatetime("bot_token_exp", future=True),
            )
            await eave.core.internal.orm.atlassian_installation.AtlassianInstallationOrm.create(
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
        response_obj = eave_ops.GetTeam.ResponseBody(**response.json())

        assert response_obj.integrations.slack is not None
        assert response_obj.integrations.slack.slack_team_id == self.anystring("slack_team_id")
        assert response_obj.integrations.slack.bot_token == self.anystring("bot_token")

        assert response_obj.integrations.atlassian is not None
        assert response_obj.integrations.atlassian.confluence_space_key == self.anystring("confluence_space")
        assert response_obj.integrations.atlassian.atlassian_cloud_id == self.anystring("atlassian_cloud_id")
        assert response_obj.integrations.atlassian.oauth_token_encoded == self.anyjson("oauth_token_encoded")

    async def test_get_team_without_integrations(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

        response = await self.make_request(
            path="/team/query",
            payload=None,
            team_id=team.id,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = eave_ops.GetTeam.ResponseBody(**response.json())

        assert response_obj.integrations.slack is None
        assert response_obj.integrations.atlassian is None
