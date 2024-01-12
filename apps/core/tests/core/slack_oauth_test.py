import http
import re
import typing
import unittest.mock
import uuid
from http import HTTPStatus

import aiohttp
from eave.core.internal.orm.account import AccountOrm
from eave.core.internal.orm.slack_installation import SlackInstallationOrm
from eave.core.internal.orm.team import TeamOrm

from eave.stdlib.config import SHARED_CONFIG
import eave.core.internal
import eave.core.internal.oauth.slack
from eave.core.internal.oauth.state_cookies import EAVE_OAUTH_STATE_COOKIE_PREFIX
from eave.core.public.requests.oauth.shared import DEFAULT_TEAM_NAME
from eave.stdlib.core_api.models.account import AuthProvider
from eave.stdlib.util import ensure_uuid
from eave.stdlib.auth_cookies import (
    EAVE_ACCOUNT_ID_COOKIE_NAME,
    EAVE_ACCESS_TOKEN_COOKIE_NAME,
)
from eave.stdlib.utm_cookies import EAVE_COOKIE_PREFIX_UTM
from .base import BaseTestCase


class TestSlackOAuthHandler(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

        self.oauth_val: eave.core.internal.oauth.slack.SlackOAuthResponse = {
            "access_token": self.anystring("access_token"),
            "refresh_token": self.anystring("refresh_token"),
            "expires_in": self.anyint("expires_in"),
            "bot_user_id": self.anystring("bot user id"),
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
            path=eave.core.internal.oauth.slack.SLACK_OAUTH_AUTHORIZE_PATH,
            sign=False,
            method="GET",
            payload=None,
        )

        assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
        assert response.cookies.get(f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.slack}")
        assert response.headers[aiohttp.hdrs.LOCATION]
        assert re.search(r"^https://slack\.com/oauth/v2/authorize", response.headers[aiohttp.hdrs.LOCATION])
        assert re.search(
            f"redirect_uri={eave.core.internal.oauth.slack.SLACK_OAUTH_CALLBACK_URI}",
            response.headers[aiohttp.hdrs.LOCATION],
        )

    async def test_slack_authorize_with_utm_params(self) -> None:
        response = await self.make_request(
            path=eave.core.internal.oauth.slack.SLACK_OAUTH_AUTHORIZE_PATH,
            sign=False,
            method="GET",
            payload={
                "utm_campaign": self.anystr("utm_campaign"),
                "gclid": self.anystr("gclid"),
                "ignored_param": self.anystr(),
            },
        )

        assert response.status_code == http.HTTPStatus.TEMPORARY_REDIRECT

        assert response.cookies.get(f"{EAVE_COOKIE_PREFIX_UTM}utm_campaign") == self.getstr("utm_campaign")
        assert response.cookies.get(f"{EAVE_COOKIE_PREFIX_UTM}gclid") == self.getstr("gclid")
        assert response.cookies.get(f"{EAVE_COOKIE_PREFIX_UTM}ignored_param") is None

    async def test_slack_callback_new_account(self) -> None:
        async with self.db_session.begin() as s:
            assert (await self.count(s, AccountOrm)) == 0
            assert (await self.count(s, SlackInstallationOrm)) == 0

        response = await self.make_request(
            path=eave.core.internal.oauth.slack.SLACK_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.slack}": self.anystring("state"),
                f"{EAVE_COOKIE_PREFIX_UTM}utm_campaign": self.anystr("utm_campaign"),
                f"{EAVE_COOKIE_PREFIX_UTM}gclid": self.anystr("gclid"),
            },
        )

        assert response.status_code == HTTPStatus.TEMPORARY_REDIRECT
        assert (
            response.cookies.get(f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.slack}") is None
        )  # Test the cookie was deleted
        assert response.headers[aiohttp.hdrs.LOCATION]
        assert (
            response.headers[aiohttp.hdrs.LOCATION]
            == f"https://slack.com/app_redirect?app={SHARED_CONFIG.eave_slack_app_id}&team={self.getstr('team.id')}"
        )

        account_id = response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME)
        assert account_id
        assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME)

        async with self.db_session.begin() as s:
            assert (await self.count(s, AccountOrm)) == 1
            assert (await self.count(s, SlackInstallationOrm)) == 1

            eave_account = await AccountOrm.one_or_none(
                session=s,
                params=AccountOrm.QueryParams(id=ensure_uuid(account_id)),
            )
            assert eave_account

            eave_team = await TeamOrm.one_or_none(
                session=s,
                team_id=eave_account.team_id,
            )
            assert eave_team

            slack_installation = await SlackInstallationOrm.one_or_none(
                session=s, slack_team_id=self.anystring("team.id")
            )
            assert slack_installation

            assert eave_account.opaque_utm_params is not None
            assert eave_account.opaque_utm_params.get("utm_campaign") == self.getstr("utm_campaign")
            assert eave_account.opaque_utm_params.get("gclid") == self.getstr("gclid")

            assert eave_account.access_token == self.anystring("authed_user.access_token")
            assert eave_account.refresh_token == self.anystring("authed_user.refresh_token")
            assert eave_account.auth_id == self.anystring("authed_user.id")
            assert eave_account.auth_provider == AuthProvider.slack
            assert eave_account.email == self.anystring("slack_user_email")
            assert eave_team.name == self.anystring("team.name")
            assert slack_installation.bot_token == self.anystring("access_token")
            assert slack_installation.bot_refresh_token == self.anystring("refresh_token")
            assert slack_installation.slack_team_id == self.anystring("team.id")
            assert slack_installation.team_id == eave_team.id

    async def test_slack_callback_new_account_without_team_name_from_slack(self) -> None:
        self.oauth_val["team"]["name"] = ""

        response = await self.make_request(
            path=eave.core.internal.oauth.slack.SLACK_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.slack}": self.anystring("state"),
            },
        )

        assert response.status_code == http.HTTPStatus.TEMPORARY_REDIRECT
        account_id = response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME)

        async with self.db_session.begin() as s:
            eave_account = await self.get_eave_account(s, id=uuid.UUID(account_id))
            assert eave_account
            eave_team = await self.get_eave_team(s, id=eave_account.team_id)
            assert eave_team
            assert eave_team.name == f"{self.anystring('slack_given_name')}'s Team"

    async def test_slack_callback_new_account_without_user_name_from_slack(self) -> None:
        self.oauth_val["team"]["name"] = ""
        self.userinfo_val.given_name = None

        response = await self.make_request(
            path=eave.core.internal.oauth.slack.SLACK_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.slack}": self.anystring("state"),
            },
        )

        assert response.status_code == http.HTTPStatus.TEMPORARY_REDIRECT
        account_id = response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME)

        async with self.db_session.begin() as s:
            eave_account = await self.get_eave_account(s, id=uuid.UUID(account_id))
            assert eave_account
            eave_team = await self.get_eave_team(s, id=eave_account.team_id)
            assert eave_team
            assert eave_team.name == DEFAULT_TEAM_NAME

    async def test_slack_callback_existing_account(self) -> None:
        async with self.db_session.begin() as s:
            assert (await self.count(s, AccountOrm)) == 0
            eave_team = await self.make_team(s)
            eave_account_before = await self.make_account(
                s,
                team_id=eave_team.id,
                auth_provider=AuthProvider.slack,
                auth_id=self.anystring("authed_user.id"),
                access_token=self.anystring("old_access_token"),
                refresh_token=self.anystring("old_refresh_token"),
            )

        response = await self.make_request(
            path=eave.core.internal.oauth.slack.SLACK_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.slack}": self.anystring("state"),
            },
        )
        assert response.status_code == http.HTTPStatus.TEMPORARY_REDIRECT

        async with self.db_session.begin() as s:
            assert (await self.count(s, AccountOrm)) == 1
            eave_account_after = await self.reload(s, eave_account_before)
            assert eave_account_after
            # Test that the tokens were updated
            assert eave_account_after.access_token == self.anystring("authed_user.access_token")
            assert eave_account_after.refresh_token == self.anystring("authed_user.refresh_token")

            # Test that the cookies were updated
            assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) == str(eave_account_after.id)
            assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == eave_account_after.access_token

    async def test_slack_callback_logged_in_account(self) -> None:
        async with self.db_session.begin() as s:
            assert (await self.count(s, AccountOrm)) == 0
            eave_team = await self.make_team(s)
            eave_account_before = await self.make_account(
                s,
                team_id=eave_team.id,
                auth_provider=AuthProvider.slack,
                auth_id=self.anystring("authed_user.id"),
                access_token=self.anystring("old_access_token"),
                refresh_token=self.anystring("old_refresh_token"),
            )

        response = await self.make_request(
            path=eave.core.internal.oauth.slack.SLACK_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.slack}": self.anystring("state"),
                EAVE_ACCOUNT_ID_COOKIE_NAME: str(eave_account_before.id),
                EAVE_ACCESS_TOKEN_COOKIE_NAME: eave_account_before.access_token,
            },
        )

        assert response.status_code == http.HTTPStatus.TEMPORARY_REDIRECT

        async with self.db_session.begin() as s:
            assert (await self.count(s, AccountOrm)) == 1
            eave_account_after = await self.reload(s, eave_account_before)
            assert eave_account_after
            # Test that the tokens were updated
            assert eave_account_after.access_token == self.anystring("authed_user.access_token")
            assert eave_account_after.refresh_token == self.anystring("authed_user.refresh_token")

            # Test that the cookies were updated
            assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) == str(eave_account_after.id)
            assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == eave_account_after.access_token

    async def test_slack_callback_logged_in_account_another_provider(self) -> None:
        async with self.db_session.begin() as s:
            assert (await self.count(s, AccountOrm)) == 0
            eave_team = await self.make_team(s)
            eave_account_before = await self.make_account(
                s,
                team_id=eave_team.id,
                auth_provider=AuthProvider.google,
                auth_id=self.anystring("google.user_id"),
                access_token=self.anystring("old_access_token"),
                refresh_token=self.anystring("old_refresh_token"),
            )

        response = await self.make_request(
            path=eave.core.internal.oauth.slack.SLACK_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.slack}": self.anystring("state"),
                EAVE_ACCOUNT_ID_COOKIE_NAME: str(eave_account_before.id),
                EAVE_ACCESS_TOKEN_COOKIE_NAME: eave_account_before.access_token,
            },
        )
        assert response.status_code == http.HTTPStatus.TEMPORARY_REDIRECT

        async with self.db_session.begin() as s:
            assert (await self.count(s, AccountOrm)) == 1
            eave_account_after = await self.reload(s, eave_account_before)
            assert eave_account_after
            # Test that the tokens were NOT updated
            assert eave_account_after.access_token == self.anystring("old_access_token")
            assert eave_account_after.refresh_token == self.anystring("old_refresh_token")

            # Test that the cookies were NOT updated
            assert response.cookies.get(EAVE_ACCOUNT_ID_COOKIE_NAME) == str(eave_account_after.id)
            assert response.cookies.get(EAVE_ACCESS_TOKEN_COOKIE_NAME) == eave_account_after.access_token

    async def test_slack_callback_invalid_state(self) -> None:
        response = await self.make_request(
            path=eave.core.internal.oauth.slack.SLACK_OAUTH_CALLBACK_PATH,
            sign=False,
            method="GET",
            payload={
                "code": self.anystring("code"),
                "state": self.anystring("state"),
            },
            cookies={
                f"{EAVE_OAUTH_STATE_COOKIE_PREFIX}{AuthProvider.slack}": self.anystring("invalid_state"),
            },
        )

        assert response.status_code == http.HTTPStatus.BAD_REQUEST

        async with self.db_session.begin() as s:
            assert (await self.count(s, AccountOrm)) == 0
            assert (await self.count(s, TeamOrm)) == 0

    async def test_urls(self):
        assert eave.core.internal.oauth.slack.SLACK_OAUTH_AUTHORIZE_PATH == "/oauth/slack/authorize"
        assert eave.core.internal.oauth.slack.SLACK_OAUTH_CALLBACK_PATH == "/oauth/slack/callback"
        assert (
            eave.core.internal.oauth.slack.SLACK_OAUTH_CALLBACK_URI
            == f"{SHARED_CONFIG.eave_public_api_base}/oauth/slack/callback"
        )
