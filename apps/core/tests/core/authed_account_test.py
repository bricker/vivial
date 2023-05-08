import typing
import unittest.mock
from http import HTTPStatus

import eave.core.internal.database as eave_db
import eave.core.internal.oauth.slack
import eave.core.internal.orm.atlassian_installation
import eave.core.internal.orm.slack_installation
import eave.core.internal.orm.team
import eave.stdlib.core_api.operations as eave_ops

from .base import BaseTestCase


class TestAuthedAccountRequests(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        def _get_userinfo_or_exception(*args: typing.Any, **kwargs: typing.Any) -> eave.core.internal.oauth.slack.SlackOAuthResponse:
            return {
                "access_token": self.anystring("access_token"),
                "refresh_token": self.anystring("refresh_token"),
                "expires_in": self.anyint("expires_in"),
                "team": {
                    "id": self.anystring("team.id"),
                    "name": self.anystring("team.name"),
                },
                "authed_user": {
                    "id": self.anystring("authed_user.id"),
                    "access_token": self.anystring("authed_user.access_token"),
                    "refresh_token": self.anystring("authed_user.refresh_token"),
                    "expires_in": self.anyint("authed_user.expires_in"),
                },
            }

        self.patch(unittest.mock.patch("eave.core.internal.oauth.slack.get_userinfo_or_exception", side_effect=_get_userinfo_or_exception))

    async def test_get_authed_account(self) -> None:
        account = await self.make_account()

        response = await self.make_request(
            path="/me/query",
            payload=None,
            account_id=account.id,
            team_id=account.team_id,
            access_token=account.access_token,
        )

        assert response.status_code == HTTPStatus.OK

        response_obj = eave_ops.GetAuthenticatedAccount.ResponseBody(**response.json())

        assert response_obj.account.id == account.id
        assert response_obj.team.id == account.team_id

    async def test_get_authed_account_with_team_integrations(self) -> None:
        team = await self.make_team()
        account = await self.make_account(team_id=team.id)

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
                confluence_space_key=self.anystring("confluence_space"),
                atlassian_cloud_id=self.anystring("atlassian_cloud_id"),
                oauth_token_encoded=self.anyjson("oauth_token_encoded"),
            )

        response = await self.make_request(
            path="/me/query",
            payload=None,
            account_id=account.id,
            team_id=account.team_id,
            access_token=account.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = eave_ops.GetAuthenticatedAccount.ResponseBody(**response.json())

    async def test_get_authed_account_team_integrations(self) -> None:
        team = await self.make_team()
        account = await self.make_account(team_id=team.id)

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
                confluence_space_key=self.anystring("confluence_space"),
                atlassian_cloud_id=self.anystring("atlassian_cloud_id"),
                oauth_token_encoded=self.anyjson("oauth_token_encoded"),
            )

        response = await self.make_request(
            path="/me/team/integrations/query",
            payload=None,
            account_id=account.id,
            team_id=account.team_id,
            access_token=account.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = eave_ops.GetAuthenticatedAccountTeamIntegrations.ResponseBody(**response.json())

        assert response_obj.integrations.slack is not None
        assert response_obj.integrations.slack.slack_team_id == self.anystring("slack_team_id")
        assert response_obj.integrations.slack.bot_token == self.anystring("bot_token")

        assert response_obj.integrations.atlassian is not None
        assert response_obj.integrations.atlassian.confluence_space_key == self.anystring("confluence_space")
        assert response_obj.integrations.atlassian.atlassian_cloud_id == self.anystring("atlassian_cloud_id")
        assert response_obj.integrations.atlassian.oauth_token_encoded == self.anystring("oauth_token_encoded")
