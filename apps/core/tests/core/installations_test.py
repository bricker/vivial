from http import HTTPStatus

import eave.stdlib.core_api.models
import eave.stdlib.core_api.operations
import eave.stdlib.core_api.operations as eave_ops

import eave.core.internal.database as eave_db
import eave.core.internal.oauth.slack
import eave.core.internal.orm.atlassian_installation
import eave.core.internal.orm.github_installation
import eave.core.internal.orm.slack_installation
import eave.core.internal.orm.team

from .base import BaseTestCase


class TestInstallationsRequests(BaseTestCase):
    async def test_get_slack_installation(self) -> None:
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

        response = await self.make_request(
            path="/integrations/slack/query",
            payload={
                "slack_integration": {
                    "slack_team_id": self.anystring("slack_team_id"),
                },
            },
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = eave_ops.GetSlackInstallation.ResponseBody(**response.json())

        assert response_obj.slack_integration.slack_team_id == self.anystring("slack_team_id")
        assert response_obj.slack_integration.bot_token == self.anystring("bot_token")

    async def test_get_slack_installation_validation_error(self) -> None:
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

        response = await self.make_request(
            path="/integrations/slack/query",
            payload={
                self.anystring(): {
                    self.anystring(): self.anystring(),
                },
            },
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    async def test_get_slack_installation_not_found(self) -> None:
        response = await self.make_request(
            path="/integrations/slack/query",
            payload={
                "slack_integration": {
                    "slack_team_id": self.anystring("slack_team_id"),
                },
            },
        )

        assert response.status_code == HTTPStatus.NOT_FOUND

        response_obj = eave.stdlib.core_api.models.ErrorResponse(**response.json())
        assert response_obj

    async def test_get_github_installation(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            await eave.core.internal.orm.github_installation.GithubInstallationOrm.create(
                session=s,
                team_id=team.id,
                github_install_id=self.anystring("github_install_id"),
            )

        response = await self.make_request(
            path="/integrations/github/query",
            payload={
                "github_integration": {
                    "github_install_id": self.anystring("github_install_id"),
                },
            },
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = eave_ops.GetGithubInstallation.ResponseBody(**response.json())

        assert response_obj.github_integration.github_install_id == self.anystring("github_install_id")

    async def test_get_github_installation_not_found(self) -> None:
        response = await self.make_request(
            path="/integrations/github/query",
            payload={
                "github_integration": {
                    "github_install_id": self.anystring("github_install_id"),
                },
            },
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json().get("status_code") == HTTPStatus.NOT_FOUND

    async def test_get_atlassian_installation(self) -> None:
        async with self.db_session.begin() as s:
            team = await self.make_team(s)

            await eave.core.internal.orm.atlassian_installation.AtlassianInstallationOrm.create(
                session=s,
                team_id=team.id,
                atlassian_cloud_id=self.anystring("atlassian_cloud_id"),
                oauth_token_encoded=self.anyjson("oauth_token_encoded"),
                confluence_space_key=self.anystring("confluence_space"),
            )

        response = await self.make_request(
            path="/integrations/atlassian/query",
            payload={
                "atlassian_integration": {
                    "atlassian_cloud_id": self.anystring("atlassian_cloud_id"),
                },
            },
        )

        assert response.status_code == HTTPStatus.OK
        response_obj = eave_ops.GetAtlassianInstallation.ResponseBody(**response.json())

        assert response_obj.atlassian_integration.atlassian_cloud_id == self.anystring("atlassian_cloud_id")
        assert response_obj.atlassian_integration.confluence_space_key == self.anystring("confluence_space")
        assert response_obj.atlassian_integration.oauth_token_encoded == self.anyjson("oauth_token_encoded")

    async def test_get_atlassian_installation_not_found(self) -> None:
        response = await self.make_request(
            path="/integrations/atlassian/query",
            payload={
                "atlassian_integration": {
                    "atlassian_cloud_id": self.anystring("atlassian_cloud_id"),
                },
            },
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        response_obj = eave.stdlib.core_api.models.ErrorResponse(**response.json())
        assert response_obj
