import typing
import unittest.mock
from http import HTTPStatus

import eave.core.internal.oauth.slack
import eave.core.internal.orm.atlassian_installation
import eave.core.internal.orm.slack_installation
import eave.core.internal.orm.team
from eave.stdlib.core_api.operations.account import GetAuthenticatedAccount, GetAuthenticatedAccountTeamIntegrations

from .base import BaseTestCase


class TestAuthedAccountRequests(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        def _get_userinfo_or_exception(
            *args: typing.Any, **kwargs: typing.Any
        ) -> eave.core.internal.oauth.slack.SlackOAuthResponse:
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

        self.patch(
            unittest.mock.patch(
                "eave.core.internal.oauth.slack.get_userinfo_or_exception", side_effect=_get_userinfo_or_exception
            )
        )

    async def test_get_authed_account(self) -> None:
        async with self.db_session.begin() as s:
            account = await self.make_account(s)

        response = await self.make_request(
            path="/me/query",
            payload=None,
            account_id=account.id,
            access_token=account.access_token,
        )

        assert response.status_code == HTTPStatus.OK

        response_obj = GetAuthenticatedAccount.ResponseBody(**response.json())

        assert response_obj.account.id == account.id
        assert response_obj.team.id == account.team_id

    async def test_get_authed_account_with_team_integrations(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            account = await self.make_account(s, team_id=team.id)

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
            path="/me/query",
            payload=None,
            account_id=account.id,
            access_token=account.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        GetAuthenticatedAccount.ResponseBody(**response.json())

    async def test_get_authed_account_team_integrations(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            account = await self.make_account(s, team_id=team.id)

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
            path="/me/team/integrations/query",
            payload=None,
            account_id=account.id,
            access_token=account.access_token,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetAuthenticatedAccountTeamIntegrations.ResponseBody(**response.json())

        assert response_obj.integrations.slack_integration is not None
        assert response_obj.integrations.slack_integration.slack_team_id == self.anystring("slack_team_id")

        assert response_obj.integrations.atlassian_integration is not None
        assert response_obj.integrations.atlassian_integration.confluence_space_key == self.anystring(
            "confluence_space"
        )
        assert response_obj.integrations.atlassian_integration.atlassian_cloud_id == self.anystring(
            "atlassian_cloud_id"
        )
