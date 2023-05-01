from http import HTTPStatus

import eave.core.internal.database as eave_db
import eave.core.internal.oauth.slack
import eave.core.internal.orm.atlassian_installation
import eave.core.internal.orm.slack_installation
import eave.core.internal.orm.team
import eave.stdlib.core_api.operations as eave_ops
import mockito

from .base import BaseTestCase


class TestAuthedAccountRequests(BaseTestCase):
    def _mock_slack_auth_response(self) -> None:
        rval: eave.core.internal.oauth.slack.SlackAuthTestResponse = {
            "bot_id": self.anystring(),
            "bot_user_id": self.anystring(),
        }

        mockito.when2(eave.core.internal.oauth.slack.auth_test_or_exception, **mockito.kwargs).thenReturn(
            self.mock_coroutine(rval)
        )

    async def test_get_authed_account(self) -> None:
        account = await self.make_account()
        self._mock_slack_auth_response()

        response = await self.make_request(
            path="/me/query",
            payload=None,
            account_id=account.id,
            team_id=account.team_id,
            access_token=account.oauth_token,
        )

        assert response.status_code == HTTPStatus.OK

        response_obj = eave_ops.GetAuthenticatedAccount.ResponseBody(**response.json())

        assert response_obj.account.id == account.id
        assert response_obj.team.id == account.team_id
        assert response_obj.team.integrations == []

    async def test_get_authed_account_with_team_integrations(self) -> None:
        team = await self.make_team()
        account = await self.make_account(team_id=team.id)
        self._mock_slack_auth_response()

        async with eave_db.async_session.begin() as db_session:
            await eave.core.internal.orm.slack_installation.SlackInstallationOrm.create(
                session=db_session,
                team_id=team.id,
                bot_refresh_token=self.anystring("bot_refresh_token"),
                bot_token=self.anystring("bot_token"),
                slack_team_id=self.anystring("slack_team_id"),
            )
            await eave.core.internal.orm.atlassian_installation.AtlassianInstallationOrm.create(
                session=db_session,
                team_id=team.id,
                confluence_space=self.anystring("confluence_space"),
                atlassian_cloud_id=self.anystring("atlassian_cloud_id"),
                oauth_token_encoded=self.anystring("oauth_token_encoded"),
            )

        response = await self.make_request(
            path="/me/query",
            payload=None,
            account_id=account.id,
            team_id=account.team_id,
            access_token=account.oauth_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = eave_ops.GetAuthenticatedAccount.ResponseBody(**response.json())
        assert response_obj.team.integrations == ["slack", "atlassian"]

    async def test_get_authed_account_team(self) -> None:
        team = await self.make_team()
        account = await self.make_account(team_id=team.id)
        self._mock_slack_auth_response()

        async with eave_db.async_session.begin() as db_session:
            await eave.core.internal.orm.slack_installation.SlackInstallationOrm.create(
                session=db_session,
                team_id=team.id,
                bot_refresh_token=self.anystring("bot_refresh_token"),
                bot_token=self.anystring("bot_token"),
                slack_team_id=self.anystring("slack_team_id"),
            )
            await eave.core.internal.orm.atlassian_installation.AtlassianInstallationOrm.create(
                session=db_session,
                team_id=team.id,
                confluence_space=self.anystring("confluence_space"),
                atlassian_cloud_id=self.anystring("atlassian_cloud_id"),
                oauth_token_encoded=self.anystring("oauth_token_encoded"),
            )

        response = await self.make_request(
            path="/me/team/query",
            payload=None,
            account_id=account.id,
            team_id=account.team_id,
            access_token=account.oauth_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = eave_ops.GetAuthenticatedAccountTeam.ResponseBody(**response.json())
        assert response_obj.team.integrations == ["slack", "atlassian"]

        assert response_obj.integrations.slack is not None
        assert response_obj.integrations.slack.slack_team_id == self.anystring("slack_team_id")
        assert response_obj.integrations.slack.bot_token == self.anystring("bot_token")

        assert response_obj.integrations.atlassian is not None
        assert response_obj.integrations.atlassian.confluence_space == self.anystring("confluence_space")
        assert response_obj.integrations.atlassian.atlassian_cloud_id == self.anystring("atlassian_cloud_id")
        assert response_obj.integrations.atlassian.oauth_token_encoded == self.anystring("oauth_token_encoded")
