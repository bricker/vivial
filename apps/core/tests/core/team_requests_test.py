from http import HTTPStatus
import http
from eave.core.internal.orm.atlassian_installation import AtlassianInstallationOrm
from eave.core.internal.orm.confluence_destination import ConfluenceDestinationOrm
from eave.core.internal.orm.connect_installation import ConnectInstallationOrm
from eave.core.internal.orm.slack_installation import SlackInstallationOrm
from eave.stdlib.core_api.models.connect import AtlassianProduct, RegisterConnectInstallationInput

from eave.stdlib.core_api.operations.team import GetTeamRequest, UpsertConfluenceDestinationAuthedRequest

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

        assert response_obj.integrations.atlassian_integration is not None
        assert response_obj.integrations.atlassian_integration.atlassian_cloud_id == self.anystring(
            "atlassian_cloud_id"
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


class UpsertConfluenceDestinationTests(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_create_confluence_destination(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            account = await self.make_account(s, team_id=team.id)

            await ConnectInstallationOrm.create(
                session=s,
                team_id=team.id,
                product=AtlassianProduct.confluence,
                client_key=self.anystring("client_key"),
                base_url=self.anystring("base_url"),
                shared_secret=self.anystring("shared_secret"),
            )

        response = await self.make_request(
            path="/me/team/destinations/confluence/upsert",
            payload={
                "confluence_destination": {
                    "space_key": self.anystring("space_key"),
                },
            },
            account_id=account.id,
            access_token=account.access_token,
        )

        assert response.status_code == http.HTTPStatus.OK
        response_obj = UpsertConfluenceDestinationAuthedRequest.ResponseBody(**response.json())
        assert response_obj.confluence_destination.space_key == self.getstr("space_key")
        assert response_obj.team.id == team.id

    async def test_update_existing_confluence_destination(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)
            account = await self.make_account(s, team_id=team.id)

            install = await ConnectInstallationOrm.create(
                session=s,
                team_id=team.id,
                product=AtlassianProduct.confluence,
                client_key=self.anystring("client_key"),
                base_url=self.anystring("base_url"),
                shared_secret=self.anystring("shared_secret"),
            )

            await ConfluenceDestinationOrm.create(
                session=s,
                team_id=team.id,
                connect_installation_id=install.id,
                space_key=self.anystring("space_key"),
            )

        response = await self.make_request(
            path="/me/team/destinations/confluence/upsert",
            payload={
                "confluence_destination": {
                    "space_key": self.anystring("updated space_key"),
                },
            },
            account_id=account.id,
            access_token=account.access_token,
        )

        assert response.status_code == http.HTTPStatus.OK
        response_obj = UpsertConfluenceDestinationAuthedRequest.ResponseBody(**response.json())
        assert response_obj.confluence_destination.space_key == self.getstr("updated space_key")

        async with self.db_session.begin() as s:
            dest_after = await ConfluenceDestinationOrm.one_or_none(session=s, connect_installation_id=install.id)
            assert dest_after is not None
            assert dest_after.space_key == self.getstr("updated space_key")
