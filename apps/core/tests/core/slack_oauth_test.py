import http
import re
import typing
import unittest.mock
import uuid
from http import HTTPStatus

import eave.stdlib.core_api

import eave.core.internal
import eave.core.internal.oauth.google
import eave.core.internal.oauth.slack
import eave.core.internal.orm.atlassian_installation
import eave.core.internal.orm.slack_installation
import eave.core.internal.orm.team

from .base import BaseTestCase


class TestSlackOAuthHandler(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        self.oauth_val: eave.core.internal.oauth.slack.SlackOAuthResponse = {
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

        self.userinfo_val = eave.core.internal.oauth.slack.SlackIdentity(
            response={
                "slack_user_id": self.anystring("authed_user.id"),
                "slack_team_id": self.anystring("team.id"),
                "email": self.anystring("slack_user_email"),
                "given_name": self.anystring("slack_given_name"),
            }
        )

        async def _get_userinfo_or_exception(
            *args: typing.Any, **kwargs: typing.Any
        ) -> eave.core.internal.oauth.slack.SlackIdentity:
            return self.userinfo_val

        self.patch(
            unittest.mock.patch(
                "eave.core.internal.oauth.slack.get_userinfo_or_exception", new=_get_userinfo_or_exception
            )
        )

        async def _get_access_token(
            *args: typing.Any, **kwargs: typing.Any
        ) -> eave.core.internal.oauth.slack.SlackOAuthResponse:
            return self.oauth_val

        self.patch(
            unittest.mock.patch("eave.core.internal.oauth.slack.get_access_token_or_exception", new=_get_access_token)
        )

        self.patch(
            unittest.mock.patch("slack_sdk.web.async_slack_response.AsyncSlackResponse", new=unittest.mock.Mock())
        )

    async def test_slack_authorize(self) -> None:
        response = await self.make_request(
            path="/oauth/slack/authorize",
            method="GET",
            payload=None,
        )

        assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
        assert response.cookies.get("ev_oauth_state_slack")
        assert response.headers["Location"]
        assert re.search(r"^https://slack\.com/oauth/v2/authorize", response.headers["Location"])
        assert re.search(
            f"redirect_uri={eave.core.internal.app_config.eave_api_base}/oauth/slack/callback",
            response.headers["Location"],
        )

    async def test_slack_callback_new_account(self) -> None:
        async with self.db_session.begin() as s:
            assert (await self.count(s, eave.core.internal.orm.AccountOrm)) == 0
            assert (await self.count(s, eave.core.internal.orm.SlackInstallationOrm)) == 0

        response = await self.make_request(
            path="/oauth/slack/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_slack": self.anystring("state"),
            },
        )
        async with self.db_session.begin() as s:
            assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
            assert not response.cookies.get("ev_oauth_state_slack")  # Test the cookie was deleted
            assert response.headers["Location"]
            assert (
                response.headers["Location"] == f"{eave.core.internal.app_config.eave_www_base}/thanks"
            )  # Default for non-whitelisted teams

            account_id = response.cookies.get("ev_account_id")
            assert account_id
            assert response.cookies.get("ev_access_token")

            assert (await self.count(s, eave.core.internal.orm.AccountOrm)) == 1
            assert (await self.count(s, eave.core.internal.orm.SlackInstallationOrm)) == 1

            eave_account = await eave.core.internal.orm.AccountOrm.one_or_none(
                session=s,
                id=uuid.UUID(account_id),
            )
            assert eave_account

            eave_team = await eave.core.internal.orm.TeamOrm.one_or_none(
                session=s,
                team_id=eave_account.team_id,
            )
            assert eave_team

            slack_installation = await eave.core.internal.orm.SlackInstallationOrm.one_or_none(
                session=s, slack_team_id=self.anystring("team.id")
            )
            assert slack_installation

            assert eave_account.access_token == self.anystring("authed_user.access_token")
            assert eave_account.refresh_token == self.anystring("authed_user.refresh_token")
            assert eave_account.auth_id == self.anystring("authed_user.id")
            assert eave_account.auth_provider == eave.stdlib.core_api.enums.AuthProvider.slack
            assert eave_team.name == self.anystring("team.name")
            assert slack_installation.bot_token == self.anystring("access_token")
            assert slack_installation.bot_refresh_token == self.anystring("refresh_token")
            assert slack_installation.slack_team_id == self.anystring("team.id")
            assert slack_installation.team_id == eave_team.id

    async def test_slack_callback_new_account_without_team_name_from_slack(self) -> None:
        self.oauth_val["team"]["name"] = ""

        response = await self.make_request(
            path="/oauth/slack/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_slack": self.anystring("state"),
            },
        )

        async with self.db_session.begin() as s:
            account_id = response.cookies.get("ev_account_id")
            eave_account = await self.get_eave_account(s, id=uuid.UUID(account_id))
            assert eave_account
            eave_team = await self.get_eave_team(s, id=eave_account.team_id)
            assert eave_team
            assert eave_team.name == f"{self.anystring('slack_given_name')}'s Team"

    async def test_slack_callback_new_account_without_user_name_from_slack(self) -> None:
        self.oauth_val["team"]["name"] = ""
        self.userinfo_val.given_name = None

        response = await self.make_request(
            path="/oauth/slack/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_slack": self.anystring("state"),
            },
        )

        async with self.db_session.begin() as s:
            account_id = response.cookies.get("ev_account_id")
            eave_account = await self.get_eave_account(s, id=uuid.UUID(account_id))
            assert eave_account
            eave_team = await self.get_eave_team(s, id=eave_account.team_id)
            assert eave_team
            assert eave_team.name == "Your Team"

    async def test_slack_callback_whitelisted_team(self) -> None:
        self.patch_dict(
            unittest.mock.patch.dict(
                "os.environ",
                {
                    "EAVE_BETA_PREWHITELISTED_EMAILS_CSV": self.anystring("slack_user_email"),
                },
            ),
        )

        response = await self.make_request(
            path="/oauth/slack/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_slack": self.anystring("state"),
            },
        )

        async with self.db_session.begin() as s:
            account_id = response.cookies.get("ev_account_id")
            assert account_id
            eave_account = await self.get_eave_account(s, id=uuid.UUID(account_id))
            assert eave_account
            eave_team = await self.get_eave_team(s, id=eave_account.team_id)
            assert eave_team

            assert eave_team.beta_whitelisted is True

            assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
            assert response.headers["Location"]
            assert response.headers["Location"] == f"{eave.core.internal.app_config.eave_www_base}/dashboard"

    async def test_slack_callback_existing_account(self) -> None:
        async with self.db_session.begin() as s:
            eave_team = await self.make_team(s)
            eave_account_before = await self.make_account(
                s,
                team_id=eave_team.id,
                auth_provider=eave.stdlib.core_api.enums.AuthProvider.slack,
                auth_id=self.anystring("authed_user.id"),
                access_token=self.anystring("old_access_token"),
                refresh_token=self.anystring("old_refresh_token"),
            )

        response = await self.make_request(
            path="/oauth/slack/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_slack": self.anystring("state"),
            },
        )

        async with self.db_session.begin() as s:
            assert (await self.count(s, eave.core.internal.orm.AccountOrm)) == 1
            eave_account_after = await self.reload(s, eave_account_before)
            assert eave_account_after
            # Test that the tokens were updated
            assert eave_account_after.access_token == self.anystring("authed_user.access_token")
            assert eave_account_after.refresh_token == self.anystring("authed_user.refresh_token")

            # Test that the cookies were updated
            assert response.cookies.get("ev_account_id") == str(eave_account_after.id)
            assert response.cookies.get("ev_access_token") == eave_account_after.access_token

    async def test_slack_callback_logged_in_account(self) -> None:
        async with self.db_session.begin() as s:
            eave_team = await self.make_team(s)
            eave_account_before = await self.make_account(
                s,
                team_id=eave_team.id,
                auth_provider=eave.stdlib.core_api.enums.AuthProvider.slack,
                auth_id=self.anystring("authed_user.id"),
                access_token=self.anystring("old_access_token"),
                refresh_token=self.anystring("old_refresh_token"),
            )

        response = await self.make_request(
            path="/oauth/slack/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_slack": self.anystring("state"),
                "ev_account_id": str(eave_account_before.id),
                "ev_access_token": eave_account_before.access_token,
            },
        )

        async with self.db_session.begin() as s:
            assert (await self.count(s, eave.core.internal.orm.AccountOrm)) == 1
            eave_account_after = await self.reload(s, eave_account_before)
            assert eave_account_after
            # Test that the tokens were updated
            assert eave_account_after.access_token == self.anystring("authed_user.access_token")
            assert eave_account_after.refresh_token == self.anystring("authed_user.refresh_token")

            # Test that the cookies were updated
            assert response.cookies.get("ev_account_id") == str(eave_account_after.id)
            assert response.cookies.get("ev_access_token") == eave_account_after.access_token

    async def test_slack_callback_logged_in_account_another_provider(self) -> None:
        async with self.db_session.begin() as s:
            eave_team = await self.make_team(s)
            eave_account_before = await self.make_account(
                s,
                team_id=eave_team.id,
                auth_provider=eave.stdlib.core_api.enums.AuthProvider.google,
                auth_id=self.anystring("google.user_id"),
                access_token=self.anystring("old_access_token"),
                refresh_token=self.anystring("old_refresh_token"),
            )

        response = await self.make_request(
            path="/oauth/slack/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_slack": self.anystring("state"),
                "ev_account_id": str(eave_account_before.id),
                "ev_access_token": eave_account_before.access_token,
            },
        )

        async with self.db_session.begin() as s:
            assert (await self.count(s, eave.core.internal.orm.AccountOrm)) == 1
            eave_account_after = await self.reload(s, eave_account_before)
            assert eave_account_after
            # Test that the tokens were NOT updated
            assert eave_account_after.access_token == self.anystring("old_access_token")
            assert eave_account_after.refresh_token == self.anystring("old_refresh_token")

            # Test that the cookies were NOT updated
            assert response.cookies.get("ev_account_id") == str(eave_account_before.id)
            assert response.cookies.get("ev_access_token") == eave_account_before.access_token

    async def test_slack_callback_invalid_state(self) -> None:
        response = await self.make_request(
            path="/oauth/slack/callback",
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                "ev_oauth_state_slack": self.anystring("invalid_state"),
            },
        )

        async with self.db_session.begin() as s:
            assert response.status_code == http.HTTPStatus.BAD_REQUEST
            assert (await self.count(s, eave.core.internal.orm.AccountOrm)) == 0
            assert (await self.count(s, eave.core.internal.orm.TeamOrm)) == 0
