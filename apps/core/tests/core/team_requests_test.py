import unittest.mock
from http import HTTPStatus
import http
from typing import Any
from eave.core.internal.oauth.slack import SlackIdentity
from eave.core.internal.orm.atlassian_installation import AtlassianInstallationOrm
from eave.core.internal.orm.connect_installation import ConnectInstallationOrm
from eave.core.internal.orm.slack_installation import SlackInstallationOrm
from eave.stdlib.core_api.models.connect import RegisterConnectInstallationInput

from eave.stdlib.core_api.operations.team import GetTeamRequest

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
        response_obj = GetTeamRequest.ResponseBody(**response.json())

        assert response_obj.integrations.slack_integration is not None
        assert response_obj.integrations.slack_integration.slack_team_id == self.anystring("slack_team_id")
        assert response_obj.integrations.slack_integration.bot_token == self.anystring("bot_token")

        assert response_obj.integrations.atlassian_integration is not None
        assert response_obj.integrations.atlassian_integration.confluence_space_key == self.anystring(
            "confluence_space"
        )
        assert response_obj.integrations.atlassian_integration.atlassian_cloud_id == self.anystring(
            "atlassian_cloud_id"
        )
        assert response_obj.integrations.atlassian_integration.oauth_token_encoded == self.anyjson(
            "oauth_token_encoded"
        )

    async def test_get_team_without_integrations(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

        response = await self.make_request(
            path="/team/query",
            payload=None,
            team_id=team.id,
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = GetTeamRequest.ResponseBody(**response.json())
        assert response_obj.team.id == team.id


class CreateConfluenceDestinationTests(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        self.userinfo_val = SlackIdentity(
            response={
                "slack_user_id": self.anystring("authed_user.id"),
                "slack_team_id": self.anystring("team.id"),
                "email": self.anystring("slack_user_email"),
                "given_name": self.anystring("slack_given_name"),
            }
        )

        async def _get_userinfo_or_exception(*args: Any, **kwargs: Any) -> SlackIdentity:
            return self.userinfo_val

        self.patch(
            unittest.mock.patch(
                "eave.core.internal.oauth.slack.get_userinfo_or_exception", new=_get_userinfo_or_exception
            )
        )

    async def test_create_confluence_destination(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            account = await self.make_account(s, team_id=team.id)

            await ConnectInstallationOrm.create(
                session=s,
                team_id=team.id,
                input=RegisterConnectInstallationInput.parse_obj(
                    {
                        "product": "confluence",
                        "client_key": self.anystring("client_key"),
                        "base_url": self.anystring("base_url"),
                        "shared_secret": self.anystring("shared_secret"),
                    }
                ),
            )

        response = await self.make_request(
            path="/me/team/destinations/confluence/create",
            payload={
                "confluence_destination": {
                    "space_key": self.anystring("space_key"),
                },
            },
            account_id=account.id,
            access_token=account.access_token,
        )

        assert response.status_code == http.HTTPStatus.OK
